# -*- coding: utf-8 -*-

# Python2.X encoding wrapper
import codecs,sys,numpy,pprint,re,random
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
from math import log10
from collections import defaultdict#, Counter

FLOAT_MIN = 2.2250738585072014
FLOAT_10EXP_MIN = -308.0
FLOAT_MAX = 1.7976931348623157
FLOAT_10EXP_MAX = 308.0



def main():
	with codecs.open('result/test.input.txt', 'r', 'utf-8') as f:
		snt = [x.strip().split(u'//') for x in f.readlines()]

	pattern = re.compile(r'\{(.+?)\}')
	for s in snt:
		if not pattern.search(u''.join(s)):
			# print 'Delete Sentence:"%s"' %u' '.join(s)
			snt.remove(s)

	V = []		#全フレーム中の語彙の異なり総数(ex dobj:you)
	V_snt = []	#各フレームごとの語彙異なり語と頻度リスト	(ex [[{'dobj:you':25},{}..],[]...])
	C = defaultdict(list)		#各フレームｖと所属するクラスタCを対応付け
	# F = [Counter() for i in range(len(snt))]
	F = [{} for i in range(len(snt))]	#python2.6ではCounterがないので…

	for v in snt:
		snt_temp = {}
		for i, w in enumerate(v):
			if w[0] == u'<':
				temp = []
				temp.append(w.split(u'>:')[0][1:])
				temp_words = {}
				for s in pattern.search(w).group()[1:-1].split(u', '):
					s_split = s.split(u':')
					temp_words[s_split[0]] = int(s_split[1])
					w_pair = u'%s:%s' %(temp[0], s_split[0])
					V.append(w_pair)
					snt_temp.update({w_pair: int(s_split[1])})
				temp.append(temp_words)
				v[i] = temp
		V_snt.append(snt_temp)

	print 'INPUT Sentences:', len(V_snt)
	V = list(set(V))
	# for i in range(len(snt)):
	# 	C[i] = []

	#全初期フレームにランダムに所属するクラスタ番号を割り当てる
	for i in range(len(snt)):
		C[random.randint(0, len(snt)-1)].append(i)

	alpha = 1	#αとβの値を決定
	beta = 20

	for I in range(100):
		for i, n in enumerate(snt):
			for k, l in C.items():
				if i in l:			#viを所属クラスタC[k]から削除
					l.remove(i)
			print 'snt[%d]'%i, C
			C_index = [k for k, l in C.items() if not l == []]
			new_i = random.choice(list(set(range(len(snt))) - set(C_index)))
			C_index.append(new_i)
			# print new_i, C_index
			P = {}
			for j in C_index:
				if j == new_i:
					P_w_f = beta - log10(len(V))*beta
					P_like = P_w_f * (len(n) - 1)
					P_prior = log10(alpha) - log10(len(snt) + alpha)
				else:
					P_like = 0
					for w in V:
						if w in V_snt[i]:
							# print w, j, C[j]
							count_f_w, count_f_t = 0, 0
							for snt_i in C[j]:
								if V_snt[snt_i].has_key(w):
									count_f_w += V_snt[snt_i][w]
								count_f_t += sum(V_snt[snt_i].values())
							# if count_f_w != 0:
							# print count_f_w, count_f_t
							log_Aw = log10(count_f_w + beta)
							log_Bw = log10(count_f_t + len(V)*beta)
							P_like += V_snt[i][w]*(log_Aw - log_Bw)

					P_prior = log10(len(C[j])) - log10(len(snt) + alpha)
				log_pst = P_prior + P_like
				P[j] = log_pst
				# if P[j] == 0.0:
					# P[j] = FLOAT_MIN
			print pp(P)

			plus_exp = -(min(P.values()) - FLOAT_10EXP_MIN)
			# plus_exp = - (sum(P.values()) / len(P))
			print plus_exp
			for index, p in P.items():
				temp_logp = P[index] + plus_exp
				P[index] = 10**temp_logp
				print P[index]

			rand =  random.uniform(0, sum(P.values()))
			total = 0
			# index = 0
			for c_index, p in P.items():
				total += p
				if total > rand:
					# if i == 1:
					print rand
					print 'add Cluster -> %d' %c_index
					C[c_index].append(i)
					if I > 50:
						if F[i].has_key(c_index):
							F[i][c_index] += 1
						else:
							F[i][c_index] = 1
					break
				# index += 1

	Result_Class = defaultdict(list)
	for index, cnt in enumerate(F):
		# Result_Class[cnt.most_common(1)[0][0]].append('snt#%d' %index)
		Result_Class[most_commom_indict(cnt)].append('snt#%d' %index)

	print "number of class: " ,len(Result_Class)
	print Result_Class

def most_commom_indict(dic):
	return sorted(dic.iteritems(), key=lambda x: x[1], reverse=True)[0][0]


import re, pprint
def pp(obj):
	pp = pprint.PrettyPrinter(indent=4, width=160)
	str = pp.pformat(obj)
	return re.sub(r"\u([0-9a-f]{4})", lambda x: unichr(int("0x"+x.group(1), 16)), str)

if __name__ == '__main__':
	main()
	