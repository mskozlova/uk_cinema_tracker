set -eux

original_filename=movies.db
backup_filename=db_backup/movies_$(date +"%Y-%m-%dT%T.%N" -u).db.zstd

if [ ! -f "$original_filename" ]; then
    echo "$original_filename does not exist."
    exit 1
fi

mkdir db_backup -p
find db_backup -mtime +30 -delete
zstd --ultra -22 $original_filename -o $backup_filename 
