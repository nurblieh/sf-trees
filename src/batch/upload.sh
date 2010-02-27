#!/bin/sh
#
# Copyright 2009 Bradley Heilbrun
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <app-host-name> <csv-file>" &>2
  exit
fi

URL="http://$1/remote_api"
CSV="$2"

python2.5 /usr/local/bin/appcfg.py upload_data --config_file=tree_loader.py \
                      --kind=SFTree \
                      --filename="$CSV" \
                      --url="$URL" \
                      --batch_size=50 \
                      --rps_limit=200 \
                      --num_threads=5 \
                      --db_filename=progress_db.sql3 \
                      ../

