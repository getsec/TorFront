import random
import string
import json


api_keys = []

total_number_of_keys_to_generate = 50
length_for_each_api_key = 128
puncuation_minus_space =  "!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"

for i in range(total_number_of_keys_to_generate):
    api_keys.append(''.join(random.SystemRandom().choice(string.ascii_letters + string.digits + puncuation_minus_space) for _ in range(128)))

with open('secrets/keys.json', 'w') as f:
    f.write(json.dumps(api_keys))


print(type(string.ascii_letters))
