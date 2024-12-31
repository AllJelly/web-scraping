from tmdbv3api import TMDb, Movie
import pandas as pd


tmdb = TMDb()
tmdb.language   = 'pt-BR'
tmdb.debug      = True
tmdb.api_key    = '6e347a3898f3f9c7250dc0a46fb27cec'

movie = Movie()

popular = movie.popular()

for p in popular:
    print(p.title)
    # print(p.id)
    # print(p.overview)
    # print(p.poster_path)