#Script for LabelMe-style json-coordinate extraction from microscope XLIF and (Pollenlabeler) DB3-database files.
#Suitable for the training of the TOFSI model (Theuerkauf et al (2023).
#Other models might require a slightly different formatting, change if needed.
#Assumes that tiff-image stacks are placed in order, e.g. the first stack should belong to microscope grid 0,0 (row 0, column 0).

############################################################
# STEP 0: Libraries
############################################################
library(xml2)
library(DBI)
library(RSQLite)
library(dplyr)
library(jsonlite)
library(tools)

############################################################
# CONFIG
############################################################
xlif_path <- "YOUR_XLIF_PATH"
db_path   <- "YOUR_DB3_PATH"
image_dir <- "YOUR_TIFF_IMAGE_PATH"
json_dir  <- "JSON_OUTPUT_FILE"


target_slide_id <- "POLLENLABELER_SLIDE_ID" #slide_id in the pollenlabeler db3_file for target slide

tiff_width_px  <- 2736
tiff_height_px <- 1824
pixel_size_um  <- 0.12 #Micrometer-pixel ratio

dir.create(json_dir, showWarnings = FALSE, recursive = TRUE)

############################################################
# STEP 1: Read XLIF and extract tile positions (ABSOLUTE µm)
############################################################
xlif <- read_xml(xlif_path)
tiles <- xml_find_all(xlif, ".//Tile")

tile_df <- tibble(
  row     = as.integer(xml_attr(tiles, "FieldY")),
  col     = as.integer(xml_attr(tiles, "FieldX")),
  PosX_um = as.numeric(xml_attr(tiles, "PosX")) * 1e6,
  PosY_um = as.numeric(xml_attr(tiles, "PosY")) * 1e6
)

############################################################
# STEP 2: Read TIFF filenames (order must match XLIF)
############################################################
tiff_files <- list.files(
  image_dir,
  pattern = "\\.tif(f)?$",
  full.names = FALSE
)

stopifnot(length(tiff_files) == nrow(tile_df))

tile_image_df <- bind_cols(tile_df, Filename = tiff_files)

############################################################
# STEP 3: Read DB3 pollen data
############################################################
con <- dbConnect(SQLite(), db_path)
d.slides <- dbReadTable(con, "Slides")
d.pollen <- dbReadTable(con, "Pollen")
d.codes  <- dbReadTable(con, "Codes")
dbDisconnect(con)

d.poll <- d.pollen %>%
  filter(SlideId == target_slide_id) %>%
  left_join(d.slides %>% select(SlideId, PathName), by = "SlideId") %>%
  left_join(d.codes, by = "SpeciesId")

############################################################
# STEP 4: Join tiles and convert to pixel coordinates
############################################################
d.poll <- d.poll %>%
  left_join(
    tile_image_df %>% select(row, col, PosX_um, PosY_um, Filename),
    by = c("Row" = "row", "Column" = "col")
  ) %>%
  mutate(
    relX_um = XOffset - PosX_um,
    relY_um = YOffset - PosY_um,
    pixelX = relX_um / pixel_size_um,
    pixelY = relY_um / pixel_size_um,
    pixelW = Width,
    pixelH = Height
  )

############################################################
# STEP 5: Write JSONs for ALL TIFFs and optionally replace label → Nonpollen
############################################################
pollen_by_tiff <- split(d.poll, d.poll$Filename)
all_classes <- c()

for (fname in tile_image_df$Filename) {
  
  df <- pollen_by_tiff[[fname]]
  
  shapes <- if (!is.null(df) && nrow(df) > 0) {
    lapply(seq_len(nrow(df)), function(i) {
      x1 <- max(0, min(df$pixelX[i], tiff_width_px))
      y1 <- max(0, min(df$pixelY[i], tiff_height_px))
      x2 <- max(0, min(df$pixelX[i] + df$pixelW[i], tiff_width_px))
      y2 <- max(0, min(df$pixelY[i] + df$pixelH[i], tiff_height_px))
      
      label <- df$Code[i]
      if (!is.null(label) && label == "???") label <- "Nonpollen" #changes your debris objects class name to 'Nonpollen', remove if not necesary
      all_classes <<- c(all_classes, label)
      
      list(
        label = label,
        line_color = NULL,
        fill_color = NULL,
        points = list(c(x1, y1), c(x2, y2)),
        shape_type = "rectangle",
        flags = list()
      )
    })
  } else {
    list()
  }
  
  json_data <- list(
    flags = list(),
    shapes = shapes,
    lineColor = list(0, 255, 0, 128),
    fillColor = list(255, 0, 0, 128),
    imagePath = fname,
    imageData = NULL
  )
  
  json_text <- toJSON(json_data, pretty = TRUE, auto_unbox = TRUE)
  writeLines(json_text, file.path(json_dir, paste0(file_path_sans_ext(fname), ".json")))
  message("Processed: ", fname)
}


############################################################
# STEP 6: Print unique pollen classes found in the created json-files
############################################################
unique_classes <- unique(all_classes)
cat("Unique classes across all JSONs:\n")
print(unique_classes)
