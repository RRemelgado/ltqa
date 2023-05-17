#-----------------------------------------------------------------------------#
# determine where script is running and install needed packages
#-----------------------------------------------------------------------------#

require("readr")
require("plyr")

#-----------------------------------------------------------------------------#
# process metadata
#-----------------------------------------------------------------------------#

# list files to process
files = list.files('source', '.csv$', full.names=T)

# setup progress bar
pb = txtProgressBar(min=0, max=length(files), style=3, width=50, char="=")

# process files
for (i in 1:length(files)) {
  
  # try column names (collection 1 and 2 might differ)
  columns = c('path','row','sensor','imageQuality1',
              'cloudCover','dayOrNight','acquisitionDate')
  
  # test if column names are valid
  ids = read_csv(files[i], n_max=1, num_threads=1, 
			show_col_types=FALSE, progress=FALSE)
  
  # use alternative column names if necessary
  columns = c('WRS Path','WRS Row','Sensor Identifier','Image Quality',
				'Land Cloud Cover','Day/Night Indicator','Date Acquired')
  
  # read data
  ids = read_csv(files[i], col_select=all_of(columns[columns %in% colnames(ids)]), 
                 show_col_types=FALSE, num_threads=1, progress=F)
  
  if (sum(colnames(ids) %in% 'Image Quality') == 0) ids$'Image Quality' = 9
  
  ids = ids[,columns]
  
  colnames(ids) = c('path','row','sensor','imageQuality',
                    'cloudCover','dayOrNight','acquisitionDate')
  
  # extract time data
  ids$year = as.numeric(substr(ids$acquisitionDate, 1, 4))
  ids$month = as.numeric(substr(ids$acquisitionDate, 6, 7))
  ids$day = as.numeric(substr(ids$acquisitionDate, 9, 10))
  
  # harmonized day/night keywords
  ids$tile_id = paste0(sprintf('%03d', ids$path), sprintf('%03d', ids$row))
  ids$dayOrNight[which(ids$dayOrNight %in% c('Day','DAY'))] = 'day'
  ids$dayOrNight[which(ids$dayOrNight %in% c('Night','NIGHT'))] = 'night'
  
  # add quality index
  ids$image_quality = (1-ids$cloudCover/100) * (ids$imageQuality/9)
  
  # subset output
  ids = ids[,c('tile_id','sensor','cloudCover','dayOrNight',
				'year','month','day','image_quality')]
  
  # write data by year (when possible, add to existing file)
  for (year in as.character(unique(ids$year))) {
    ind = which(ids$year == as.numeric(year))
    oname = paste0('./meta/', year, '.csv')
    if (!file.exists(oname)) {
      write_csv(ids[ind,], oname, progress=F)
    }else {
      write_csv(ids[ind,], oname, append=T, col_names=F, progress=F)
    }
  }
  
  # remove heavy inputs
  rm(ids, year, month, day, ind, test)
  
  # clear garbage left by readr
  gc()
  
  # report on progress
  setTxtProgressBar(pb, i)
  
}

#-----------------------------------------------------------------------------#
# build aggregation functions
#-----------------------------------------------------------------------------#

f1 = function(x,y) {
  ns = sapply(1:12, function(m) {
    ind = which(x == m)
    if (length(ind) > 0) return(max(y[ind])) else return(0)
  })
  return(sum(ns)/12)
  
}
  
f2 = function(x,y) {
  ns = sapply(1:12, function(m) {
    ind = which(x == m)
    if (length(ind) > 0) return(max(y[ind])) else return(0)
  })
  a = sum(ns[1:6])
  b = sum(ns[7:12])
  return((b-a) / (b+a))
}

#-----------------------------------------------------------------------------#
# aggregate metadata
#-----------------------------------------------------------------------------#

# list files to aggregate
files = list.files('meta', '.csv', full.names=T)

# extract ID's of land tiles
tiles = sprintf('%06d', read.csv('wrs/wrs2_land_tiles.csv', stringsAsFactors=F)$tiles)

# setup progress bar
pb = txtProgressBar(min=0, max=length(files), style=3, width=50, char="=")

for (i in 1:length(files)) {
  
  ids = read_csv(files[i], progress=FALSE, show_col_types=F)
  
  # subset data frame for land tiles
  ids = ids[which(ids$tile_id %in% tiles),]
  
  # aggregate data.frame on a monthly basis
  odf = ddply(ids[which(ids$image_quality > 0),], .(tile_id,year,dayOrNight), 
              summarise, 
              total_quality=sum(image_quality), 
              max_quality=max(image_quality), 
              image_count=length(tile_id), 
              month_count=length(unique(month)),
              distribution_quality=f1(month,image_quality), 
              distribution_balance=f2(month,image_quality))
  
  # save aggregated metadata
  bname = strsplit(basename(files[i]), '[.]')[[1]][1]
  write_csv(odf, paste0('quality/', bname, '_qa.csv'), progress=F)
  
  # remove heavy inputs
  rm(ids, odf)
  
  # clear garbage left by readr
  gc()
  
  # report on progress
  setTxtProgressBar(pb, i)
  
}

# combine yearly outputs
files = list.files('quality', '.csv', full.names=T)
ids = do.call(rbind, lapply(files, function(i) read.csv(i, colClasses='character')))
write.csv(ids, 'LTQA_metadata.csv', row.names=F)
