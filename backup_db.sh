set -eux
backup_filename=db_backup/movies_$(date +"%Y-%m-%dT%T.%N" -u).db.zstd
find db_backup -mtime +30 -delete && zstd --ultra -22 movies.db -o $backup_filename 
