make
if [ ! -e text8 ]; then
  wget http://mattmahoney.net/dc/text8.zip -O text8.gz
  gzip -d text8.gz -f
fi
time ./OptRank3 -train text8 -output OptRank3_vectors -cbow 1 -size 300 -window 8 -negative 15 -hs 0 -sample 1e-4 -threads 20 -min-count 5 -binary 1 -iter 10
