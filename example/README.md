# examples


```
# test gem2bfm
python3 ../GEM_toolkit.py  gem2bfm  -c test_gem2bfm.json -o test_g

# test heatmap
python3 ../GEM_toolkit.py  heatmap  -c test_gem2bfm.json -o test_h

# test apply_affinematrix
python3 ../GEM_toolkit.py  apply_affinematrix  -c test_affine.json -i example_bfm_5658 -o test_a
# test model3d
python3 ../GEM_toolkit.py model3d -i test_a -r cluster_56_58.txt -o test_m
```
