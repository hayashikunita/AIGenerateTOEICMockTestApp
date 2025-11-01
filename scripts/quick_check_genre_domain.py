import sys
sys.path.insert(0, '.')
import toeic_generator as tg

seed=20251101
print('--- P7 short, genre=press_release, domain=finance ---')
res = tg.generate_dataset(per_part=3, parts=[7], seed=seed, p7_length='short', genre='press_release', domain='finance')
for q in res['parts'][0]['questions']:
    print(q['context']['passage'])

print('\n--- P6 ad_type check, domain=hospitality ---')
res2 = tg.generate_dataset(per_part=1, parts=[6], seed=seed, genre=None, domain='hospitality')
print(res2['parts'][0]['questions'][0]['context']['text'])

print('\n--- P5 nouns/depts check, domain=education ---')
res3 = tg.generate_dataset(per_part=1, parts=[5], seed=seed, genre=None, domain='education')
print(res3['parts'][0]['questions'][0]['stem'])
print('OK')
