original_string="livecodebench_easy@livecodebench_medium@livecodebench_hard"
result_string=$(echo "$original_string" | sed 's/@/ /g')
echo "$result_string"