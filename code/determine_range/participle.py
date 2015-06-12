import jieba
import sys

def main():
	company_file_name = '../../data/cleanData.txt'
	company_file = open(company_file_name, 'r').readlines()

	word_stat = {}
	for company_record in company_file:
		cmpn_range = eval(company_record)['cmpn_range']
		print cmpn_range
		segments = jieba.cut_for_search(cmpn_range)
		for word in segments:
			if not word_stat.has_key(word):
				word_stat[word] = 0
			word_stat[word] += 1

	sys.exit(0)
	word_stat = sorted(word_stat.iteritems(), key = lambda d: d[1], reverse = True)

	for word, freq in word_stat:
		print word.encode('utf-8'), freq


if __name__ == '__main__':
	main()
