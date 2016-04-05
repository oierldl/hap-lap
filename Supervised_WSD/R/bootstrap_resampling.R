library(ggplot2)
library(reshape2)
library(plyr)


###

readkey <- function(){
  cat ("Press C and [enter] to continue:")
	b <- scan("stdin", character(), n=1, quiet=T)
}


join_files <- function(main_dir, words, ext, xval){
	df = data.frame()
	for (w in words){
		if (xval == 0){
			filename = paste(w, ext, sep=".")
			df = rbind(df, read.table(paste(main_dir, w, filename, sep="/"), header=F, sep="\t"))
		}else{
			for (x in c(1:xval)){
				fold = paste("f", x, sep="")
				filename = paste(w, fold, ext, sep=".")
				df = rbind(df, read.table(paste(main_dir, w, filename, sep="/"), header=F, sep="\t"))
			}
		}
	}
	return(df)
}

fscore <- function(predict, true){
	predict = as.vector(predict)
	true = as.vector(true)
	retrieved <- length(predict)
	gs <- length(true)
	prec = sum(predict == true) / retrieved
	recall = sum(predict == true) / gs
	fs = 2*prec*recall / (prec + recall)
	return(fs)
}


#### main ####
args <- commandArgs(trailingOnly=TRUE)
sys1_name = args[1] 
sys2_name = args[2]

gs_all_f = "../data/amt-sense-mt-2013/gs.ids.all.tsv"
gs = read.table(gs_all_f, header=F, sep="\t")

res_dir = "../results"
word_f = "../data/amt-sense-mt-2013/words.txt"
words = read.table(word_f) 
sys1_ext = paste(sys1_name, "out", sep =".")
xval = 3
sys1_ans = join_files(res_dir, words[,1], sys1_ext, xval) 
all_ans = merge(gs, sys1_ans, c(1))

sys2_ext = paste(sys2_name, "out", sep =".")
sys2_ans = join_files(res_dir, words[,1], sys2_ext, xval) 
all_ans = merge(all_ans,sys2_ans, c(1))
colnames(all_ans) = c("id", "gs", sys1_name, sys2_name)

obs_fs1 =  fscore(all_ans[,3], all_ans$gs)
obs_fs2 =  fscore(all_ans[,4], all_ans$gs)
diff_observed = obs_fs2 - obs_fs1

n = nrow(all_ans)
number_of_replicates = 1000
sys1_bootstrap = NULL
sys2_bootstrap = NULL
diff_bootstrap = NULL
cat(paste("number of replicates", number_of_replicates, sep=": "))
cat("\n")
for (i in 1:number_of_replicates){
	bind = sample(c(1:n), length(all_ans$id), TRUE)
	bootstrap = all_ans[bind,]
	fs1 =  fscore(bootstrap[,3], bootstrap$gs)
	
	bind = sample(c(1:n), length(all_ans$id), TRUE)
	bootstrap = all_ans[bind,]
	fs2 =  fscore(bootstrap[,4], bootstrap$gs)

	sys1_bootstrap[i] = fs1
	sys2_bootstrap[i] = fs2
	
	diff_bootstrap[i] = fs2 - fs1
}

df = data.frame( system = c(rep(sys1_name, number_of_replicates), rep(sys2_name, number_of_replicates)),
				 fscore = c(sys1_bootstrap, sys2_bootstrap))


#### PLOT DENSITY ####
cdf = ddply(df, "system", summarise, fscore_mean = mean(fscore))

x11()
cat("\n")
cat("[INFO] Plotting density-plot\n")
p = ggplot(df, aes(fscore, fill = system))
p = p + geom_density(alpha = 0.75)
p = p + geom_vline(data=cdf, aes(xintercept = fscore_mean, colour = system), linetype="dashed")
p = p + theme(legend.position="top")
p = p + labs(fill = "System", title = "Bootstrapped Samples")
p = p + xlab("Fscore")
print(p)

cat("\n")
readkey()

##### CONFIDENCE INTERVAL ####
alpha = 0.05
ci = t(data.frame(quantile(diff_bootstrap, c(alpha/2, 1 - alpha/2))))
cat("\n")
cat("[INFO] Confidence intervals\n")
cat("\n")
cat("  ")
cat(paste(sys1_name, sprintf("%0.3f",obs_fs1), sep =": ")) 
cat(" fscore\n")
cat("  ")
cat(paste(sys2_name, sprintf("%0.3f",obs_fs2), sep =": ")) 
cat(" fscore\n")
cat("  ")
cat(paste("Observed differences:", sprintf("%0.3f", diff_observed), sep=" "))
cat("\n")
cat("  ")
interval = paste(sprintf("%0.3f", ci[1]), sprintf("%0.3f", ci[2]), sep=" - ")
cat(paste("Confidence intervals:", interval, sep=" "))
cat("\n")
cat("\n")

## DIFFERENCES BETWEEN MEANS OF BOOTSTRAPPED SAMPLES
df1 = data.frame (diff_bootstrap)

lines = c (diff_observed, mean(diff_bootstrap), ci[1], ci[2])
names = c ("Observed", "Bootstrapped", "CI Lower", "CI Upper")

df2 = data.frame(names, lines)

colors = c("#984ea3", "#ff7f00", "#e41a1c", "#377eb8")

cat("\n")
cat("[INFO] Plotting differences between means of bootstrapped samples\n")
p = ggplot()
p = p + geom_density (data = df1, aes(diff_bootstrap), fill = "#4daf4a", alpha = 0.75)
p = p + geom_vline   (data = df2, aes(xintercept=lines, colour=names), linetype=c("solid", "dashed", "dashed", "dashed"), size=c(1.5, 0.5, 0.5, 0.5))
p = p + scale_colour_manual(values = colors)
p = p + theme(legend.position="top")
p = p + labs(title = "Bootstrapped Differences")
p = p + xlab("Differences")
print(p)

readkey()

## NULL DIFERENCES

# Difference between means under null hypothesis (i.e., zero)
diff_null = diff_bootstrap - mean(diff_bootstrap)

df = data.frame(diff_null)

critical.index = max(number_of_replicates * alpha / 2, 1)
critical.value.left = diff_null[order(diff_null)][critical.index]
critical.value.right = diff_null[order(diff_null, decreasing=TRUE)][critical.index]

cat("\n")
cat("[INFO] Plotting Null diffences\n")
p = ggplot()
p = p + geom_density(data = df, aes(diff_null), fill = "#4daf4a", alpha = 0.75)
p = p + geom_vline(xintercept=diff_observed, colour = "black", linetype="solid", size=0.5)
p = p + geom_vline(xintercept=critical.value.left, colour = "red", linetype="solid", size=0.5)
p = p + geom_vline(xintercept=critical.value.right, colour = "red", linetype="solid", size=0.5)
p = p + geom_vline(data=df, aes(xintercept=mean(diff_null)), colour="blue", linetype="dashed", size=0.5)
p = p + labs(title = "Null Differences")
p = p + xlab("Differences")
print(p)


## P-VALUE
cat("\n")

pvalue = sum(abs(diff_null) >= abs(diff_observed)) / number_of_replicates
cat(paste("  P-value: ", pvalue, sep=""))
cat("\n")
cat("\tIf P-value < 0.05\n")
cat("\tReject null hypothesis")
cat("\n")
readkey()
