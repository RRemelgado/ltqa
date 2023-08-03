# Landsat Quality Assessment (LTQA)
We developed a suite of quality metrics that characterize the annual and year-to-year frequency of satellite observations, their year-to-year recurrence, and their within-year distribution. These equate the quality of individual observations as reported by the data providers, and limitations to the usability of these data caused by cloud cover.

Here, we provided code for the calculation of these metrics (see subfolder **LTQA**), as well as code to analyse the source metadata (see subfolder **meta**), which is a required initial step.



## List of calculated metrics
* <i>nrTiles</i> - Number of Landsat tiles used to compute quality metric.
* <i>imageFrequency</i> - Number of collected images.
* <i>monthFrequency</i> - Number of months with collected images.
* <i>maxQuality</i> - Maximum image quality.
* <i>totalQuality</i> - Number of collected images, weighted by the quality of each image.
* <i>lastYear</i> - Closest year with usable data, from the start of the time-series to the reference year.
* <i>distributionBalance</i> - Average of the maximum monthly image quality.
* <i>distributionQuality</i> - Ratio between the distribution balance of the first and second half of the year.
