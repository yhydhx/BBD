import jieba
import sys


def range_trans(origin_range):
	if len(str(origin_range)) == 3:
		head = int(str(origin_range)[0])
		if 1 <= head <= 5:
			return 'A'
		elif 6 <= head <= 9:
			return 'B'
	elif len(str(origin_range)) == 4:
		head = int(str(origin_range)[:2])
		if 10 <= head <= 12:
			return 'B'
		elif 13 <= head <= 43:
			return 'C'
		elif 44 <= head <= 46:
			return 'D'
		elif 47 <= head <= 50:
			return 'E'
		elif 51 <= head <= 52:
			return 'F'
		elif 53 <= head <= 60:
			return 'G'
		elif 61 <= head <= 62:
			return 'H'
		elif 63 <= head <= 65:
			return 'I'
		elif 66 <= head <= 69:
			return 'J'
		elif head == 70:
			return 'K'
		elif 71 <= head <= 72:
			return 'L'
		elif 73 <= head <= 75:
			return 'M'
		elif 76 <= head <= 78:
			return 'N'
		elif 79 <= head <= 81:
			return 'O'
		elif head == 82:
			return 'P'
		elif 83 <= head <= 84:
			return 'Q'
		elif 85 <= head <= 89:
			return 'R'
		elif 90 <= head <= 95:
			return 'S'
		elif head == 96:
			return 'T'



def main():
	company_names = {}
	company_ranges = {}
	company_range_codes = {}
	company_range_alpha = {}
	get_training_set(company_names, company_ranges, company_range_codes, company_range_alpha)
	features = {}
	get_features(features)
	generate_data(company_ranges, company_range_alpha, features)


def generate_data(company_ranges, company_range_alpha, features):
	fout = open('temp.txt','w')
	print len(features)
	cnt = 0
	for company_name in company_range_alpha:
		input_values = [0] * len(features)
		company_range = company_ranges[company_name]
		segments = jieba.cut_for_search(company_range)
		for word in segments:			
			if features.has_key(word):
				input_values[features[word]] = 1
				cnt += 1
				print 'hit', cnt
			input_values += [company_range_alpha[company_name]]
	input_values = map(lambda d:str(d), input_values)
	fout.write('\t'.join(input_values) + '\n')


def get_features(features):
	feature_file_name = 'out1.txt'
	feature_file = open(feature_file_name, 'r')
	feature_id = 0
	for feature_record in feature_file:
		feature_name = feature_record.split()[0]
		features[feature_name] = feature_id
		feature_id += 1


def get_training_set(company_names, company_ranges, company_range_codes, company_range_alpha):
	company_file_name = '../../data/cleanData.txt'
	company_file = open(company_file_name, 'r').readlines()

	for company_record in company_file:
		company_name = eval(company_record)['cmpn_name']	
		company_range = eval(company_record)['cmpn_range']
		company_ranges[company_name] = company_range
		company_names[company_name] = True
	
	train_company_file_name = '../../data/cmpn_range_train.txt'
	train_company_file = open(train_company_file_name, 'r').readlines()

	for company_record in train_company_file:
		try:
			company_name = company_record.split(',')[1]
			if company_names.has_key(company_name):
				company_names[company_name] = False
				company_range_alpha[company_name] = range_trans(company_record.strip().split(',')[2])
				company_range_codes[company_name] = company_record.strip().split(',')[2]
		except:
			pass

	#for company_name in company_names:
	#	if company_names[company_name] == False:
	#		print company_name, company_ranges[company_name]
	#		print company_name, company_range_alpha[company_name], company_range_codes[company_name]
	#print cnt



if __name__ == "__main__":
	main()
