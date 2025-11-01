import sys
sys.path.insert(0, '.')
import toeic_generator as tg

seed = 20251101
# Part 5
p5 = tg.generate_dataset(per_part=1, parts=[5], seed=seed)
q5 = p5['parts'][0]['questions'][0]
print('P5:', q5['stem'])
# Part 6
p6 = tg.generate_dataset(per_part=1, parts=[6], seed=seed)
q6 = p6['parts'][0]['questions'][0]
print('P6:', q6['context']['text'][:100])
# Part 7
p7 = tg.generate_dataset(per_part=1, parts=[7], seed=seed, p7_length='short')
q7 = p7['parts'][0]['questions'][0]
print('P7:', q7['context']['passage'][:120])
print('OK')
