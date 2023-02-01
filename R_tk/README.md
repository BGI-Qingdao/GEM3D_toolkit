## misc R scripts for format convertion

### STOmics_seurat.only_gem2rds.R 

* Brief: Convert GEM to Seurat rds by group spots into bins
* Author: Zhang Rui (zhangrui7@genomics.cn)
* Example:

```
Rscript STOmics_seurat.only_gem2rds.R -i test.gem\
                                      -b 50 -s Test1\
                                      -o test 2>test1.log
```

