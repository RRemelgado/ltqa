#-----------------------------------------------------------------------------#
# load arguments / modules
#-----------------------------------------------------------------------------#

require(optparse)
require(multispatialCCM)

# define arguments
option_list = list(
  make_option(c("-t", "--size"), action="store", default=NA, 
              type='integer', help="temporal window size"),
  make_option(c("-i", "--index"), action="store", default=NA, 
              type='integer', help="file index"), 
  make_option(c("-s", "--file"), action="store", default=NA, 
              type='character', help="path to file with samples")
)

opt = parse_args(OptionParser(option_list=option_list))

# recover argument
time_size = opt$t
index = opt$i
input_file = opt$s

#-----------------------------------------------------------------------------#
# read samples used for the CCM analysis
#-----------------------------------------------------------------------------#

ids = read.csv(input_file)

#-----------------------------------------------------------------------------#
# check  if samples are available
#-----------------------------------------------------------------------------#

if (sum(complete.cases(ids)) == 0) {
	print("no samples available")
	exit()
}
  
#-----------------------------------------------------------------------------#
# find optimal embeddding dimension
#-----------------------------------------------------------------------------#

e = sapply(seq(1,time_size-2), function(e) SSR_pred_boot(ids$a, E=e)$rho)
e = round(ea*100)
e = which(ea == max(ea, na.rm=T))[1]

#-----------------------------------------------------------------------------#
# test for causal relationships
#-----------------------------------------------------------------------------#

# run spatial CCM
v = CCM_boot(ids$a, ids$b, e, iterations=10)

# Test for significant causal signal and record rho
d = data.frame(iso3=iso3, 
				pvalue=ccmtest(ca,ca)[[2]], rho=ca$rho[length(ca$rho)],
				nr_samples=length(unique(ids$id)), embedding=e)

# save results of the analysis
oname = file.path(dirname(input_file), paste0(strsplit(basename(input_file), "[.]")[[1]][1], "_ccm.csv"))
write.csv(d, oname, row.names=F)
