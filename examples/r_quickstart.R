# Quickstart: load the moratorium inventory and answer common questions.
#
# Run with:  Rscript examples/r_quickstart.R
# Or read the URL directly (no clone required):
#
#   df <- read.csv("https://raw.githubusercontent.com/mjbommar/moratorium-data-2026/main/data/moratorium_inventory.csv")

df <- read.csv("data/moratorium_inventory.csv", stringsAsFactors = FALSE)

cat(sprintf("Total moratoria: %d\n", nrow(df)))
cat(sprintf("States with moratoria: %d\n\n", length(unique(df$state))))

cat("Top 10 states by moratorium count:\n")
print(sort(table(df$state), decreasing = TRUE)[1:10])

cat("\nMost common jurisdiction types:\n")
print(sort(table(df$jurisdiction_type), decreasing = TRUE)[1:6])

# Sector mentions
contains_any <- function(text, kws) {
  any(sapply(kws, function(k) grepl(k, text, ignore.case = TRUE)))
}
combined <- paste(df$trigger, df$legal_basis, df$jurisdiction)
cat("\nSector mention counts:\n")
cat(sprintf("  Data center: %d\n", sum(sapply(combined, contains_any, c("data center","data centre")))))
cat(sprintf("  Cryptocurrency mining: %d\n", sum(sapply(combined, contains_any, c("crypto","mining","digital asset")))))
cat(sprintf("  Battery storage: %d\n", sum(sapply(combined, contains_any, c("battery","bess","energy storage")))))
cat(sprintf("  Solar: %d\n", sum(sapply(combined, contains_any, c("solar")))))
cat(sprintf("  Wind: %d\n", sum(sapply(combined, contains_any, c("wind")))))

# Year of adoption
df$year <- sub(".*?(20\\d{2}).*", "\\1", df$date_enacted)
df$year[df$year == df$date_enacted] <- NA
cat("\nAdoptions by year (where parseable):\n")
print(sort(table(df$year)))
