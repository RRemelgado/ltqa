# Landsat Quality Assessment (LTQA)
We developed a suite of quality metrics that characterize the annual and year-to-year frequency of satellite observations, their year-to-year recurrence, and their within-year distribution. These equate the quality of individual observations as reported by the data providers, and limitations to the usability of these data caused by cloud cover.

Here, we provided code for the calculation of these metrics (see subfolder **LTQA**), as well as code to analyse the source metadata (see subfolder **meta**), which is a required initial step.

## List of calculated metrics
•	nrTiles - Number of Landsat tiles used to compute quality metric.
•	imageFrequency - Number of collected images.
•	monthFrequency - Number of months with collected images.
•	maxQuality - Maximum image quality.
•	totalQuality - Number of collected images, weighted by the quality of each image.
•	lastYear - Closest year with usable data, from the start of the time-series to the reference year.
•	distributionBalance - Average of the maximum monthly image quality.
•	distributionQuality - Ratio between the distribution balance of the first and second half of the year.
