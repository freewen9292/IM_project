#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, time
import numpy as np
import pandas as pd
import random as rd
import tool.functions.gene_alg_new as gen
from tool.functions.CSR_order import CSR_ORDER
from tool.functions.LIMIT_ORDER import LIMIT_ORDER
from tool.functions.CONFIRM import confirm
from tool.final_score import final_score
from tool.tool import ERROR
import tool.tool as tl
import datetime, calendar, sys, copy

#========================================================================#
# Global Variables
#========================================================================#
# 產生親代的迴圈數
parent = 100	    # int
ordernum = 1        #limit_order的排序數量
cutpoint = 5       #不同安排方式的切分點
#基因演算法的世代數量
generation = 1000
mutate_prob = 0.05
shuffle = False
LACK = tl.nE
SURPLUS = tl.nE * 0.5
NIGHT = tl.P2_t
BREAKCOUNT = tl.nE * tl.nW
NOON = tl.P4_t
IGNORE = True

# 生成Initial pool的100個親代
INITIAL_POOL = []
#=======================================================================================================#
#=======================================================================================================#
tstart_0 = time.time()  #計時用

#測試檔案檔名 - 沒有要測試時請將TestPath留空白
# TestPath = ""
EmployeeTest = tl.EmployeeTest
AssignTest = tl.AssignTest
NeedTest = tl.NeedTest
U_ttest = tl.U_ttest

# =============================================================================#
# Parameters
# =============================================================================#
dir_name = tl.DIR

# -------Time-------#
year  = tl.YEAR
month = tl.MONTH

# -------number-------#
nEMPLOYEE = tl.nE                  #總員工人數
nDAY      = tl.nD                  #總日數
nK        = tl.nK                  #班別種類數
nSK       = tl.nSK                 #技能種類數
nT        = tl.nT                  #總時段數
nR        = tl.nR                  #午休種類數
nW        = tl.nW                  #總週數
mDAY      = tl.mDAY

miniresult = 100000000*nEMPLOYEE*nDAY*nT #親代最佳分數

# -----基礎項目---------#
P0, P1, P2, P3, P4 = tl.P          #目標式中的調整權重(lack, surplus, nightCount, breakCount, noonCount)
timelimit     = tl.TIME_LIMIT
#timelimit = 1000000000
Posi       = tl.POSI_list

# -------表格---------#
CONTAIN = tl.CONTAIN               #CONTAIN_kt - 1表示班別k包含時段t，0則否
DEMAND = tl.DEMAND                 #DEMAND_jt - 日子j於時段t的需求人數
ASSIGN = tl.ASSIGN                 #ASSIGN_ijk - 員工i指定第j天須排班別k，形式為 [(i,j,k)]
assign_par = tl.assign_par
EMPLOYEE_t = tl.Employee_t
E_NAME = tl.NAME_list

# -------list---------#
LMNIGHT  = tl.LastWEEK_night       #LMNIGHT_i - 表示員工i在上月終未滿一週的日子中曾排幾次晚班
FRINIGHT = tl.LastDAY_night        #FRINIGHT_i - 1表示員工i在上月最後一工作日排晚班，0則否
nightdaylimit = EMPLOYEE_t['night_perWeek']
Shift_name = tl.CLASS_list
SKILL_list = tl.SKILL_list

# -----排班特殊限制-----#
LOWER = tl.LOWER                   #LOWER - 日期j，班別集合ks，職位p，上班人數下限
UPPER = tl.UPPER                   #UPPER - 員工i，日子集合js，班別集合ks，排班次數上限
PERCENT = tl.PERCENT               #PERCENT - 日子集合，班別集合，要求占比，年資分界線
SKILL = tl.NOTPHONE_CLASS
SKILL_SPECIAL = tl.NOTPHONE_CLASS_special

# -----新  特殊班別一定人數--------------#
NOTPHONE_CLASS = tl.NOTPHONE_CLASS                     # 特殊班別每天人數相同
NOTPHONE_CLASS_special = tl.NOTPHONE_CLASS_special     # 特殊班別假日後一天人數不同
Upper_shift = tl.Upper_shift                           # 特殊班別每人排班上限


# =============================================================================#
# Sets
# =============================================================================#
EMPLOYEE = [tmp for tmp in range(nEMPLOYEE)]    #EMPLOYEE - 員工集合，I=0,…,nI 
DAY = [tmp for tmp in range(nDAY)]              #DAY - 日子集合，J=0,…,nJ-1
TIME = [tmp for tmp in range(nT)]               #TIME - 工作時段集合，T=1,…,nT
BREAK = [tmp for tmp in range(nR)]              #BREAK - 午休方式，R=1,…,nR
WEEK = [tmp for tmp in range(nW)]               #WEEK - 週次集合，W=1,…,nW
SHIFT = [tmp for tmp in range(nK)]              #SHIFT - 班別種類集合，K=1,…,nK ;0代表休假
 
# -------員工集合-------#
E_POSITION  = tl.E_POSI_set                    #E_POSITION - 擁有特定職稱的員工集合，POSI=1,…,nPOSI
E_SKILL     = tl.E_SKILL_set                   #E_SKILL - 擁有特定技能的員工集合，SKILL=1,…,nSKILL
E_SENIOR    = tl.E_SENIOR_set                  #E_SENIOR - 達到特定年資的員工集合    

# -------日子集合-------#
DATES = tl.DATE_list
DAYset = tl.D_WDAY_set                         #DAYset - 通用日子集合 [all,Mon,Tue...]
D_WEEK = tl.D_WEEK_set
WEEK_of_DAY = tl.WEEK_list                     #WEEK_of_DAY - 日子j所屬的那一週
VACnextdayset = tl.AH_list                     #VACnextdayset - 假期後或週一的日子集合
NOT_VACnextdayset = tl.NAH_list 

# -------班別集合-------#
SHIFTset= tl.K_CLASS_set                       #SHIFTset - 通用的班別集合，S=1,…,nS
SKILLset= tl.SK_CLASS_set                       #SKILLset - 技能與班別的對應集合，SK=1,…,nSK
S_NIGHT = SHIFTset['night']                     #S_NIGHT - 所有的晚班
S_NOON = SHIFTset['noon']                       #S_NOON - 所有的午班
S_BREAK =tl.K_BREAK_set


#============================================================================#
#Variables

work = {}  #work_ijk - 1表示員工i於日子j值班別為k的工作，0 則否 ;workij0=1 代表員工i在日子j休假
for i in range(nEMPLOYEE):
    for j in range(nDAY):
        for k in range(nK):
            work[i, j, k] = False  


#Test Variables
lack = {}  #y_jt - 代表第j天中時段t的缺工人數
for j in range(nDAY):
    for t in range(nT):
        lack[j, t] = 0
        
surplus = 0 #每天每個時段人數與需求人數的差距中的最大值
nightCount = 0 #員工中每人排晚班總次數的最大值

breakCount = {}  #breakCount_iwr - 1表示員工i在第w周中在午休時段r有午休，0則否
for i in range(nEMPLOYEE):
    for w in range(nW):
        for r in range(nR):
            breakCount[i, w, r] = False

noonCount = 0 #員工中每人排午班總次數的最大值


#========================================================================#
# class
#========================================================================#
class Pool():
    def __init__(self, result, df_x1):
        #result: 目標式結果
        self.result = result
        #df_x1 : 員工班表(整數班別)
        self.df_x1 = df_x1
	

#========================================================================#
# ABLE(i,j,k): 確認員工i在日子j是否可排班別k 
#========================================================================#
def ABLE(this_i,this_j,this_k,consider=False):
    ans = True
    
    #only one work a day
    for k in SHIFT:
        if(work[this_i,this_j,k] == 1) and (k != this_k):    
            ans = False
            return ans
    #被指定的排班及當天被排除的排班
    for tmp in ASSIGN:
        if(tmp[0]==this_i):
            if(tmp[1]==this_j):
                #被指定的排班
                if(tmp[2]==this_k):
                    return ans
                else:
                    ans = False
                    return ans
    
    #判斷是否正在排晚班
    arrangenightshift = False
    for tmp in S_NIGHT:
        if(this_k == tmp):
            arrangenightshift = True
            
    #正在排晚班才進去判斷
    if(arrangenightshift == True):
        #no continuous night shift:
        
        if(this_j!=0 and this_j!=nDAY-1): #非第一天或最後一天
            for tmp in S_NIGHT:
                if(work[this_i,this_j-1,tmp] == 1):
                    ans = False
                    return ans
                if(work[this_i,this_j+1,tmp] == 1):
                    ans = False
                    return ans
        elif (this_j==nDAY-1):           #最後一天
            for tmp in S_NIGHT:
                if(work[this_i,this_j-1,tmp] == 1):
                    ans = False
                    return ans
        else:                             #第一天
            if(FRINIGHT[this_i] == 1):
                ans = False
                return ans
            for tmp in S_NIGHT:
                if(work[this_i,this_j+1,tmp] == 1):
                    ans = False
                    return ans
        #no too many night shift a week:
        whichweek = WEEK_of_DAY[this_j]
        #非第一週
        if(whichweek!=0):
            countnightshift = 0
            for theday in D_WEEK[whichweek]:
                for tmp in S_NIGHT:
                    if(work[this_i,theday,tmp] == 1):
                        if(theday == this_j and tmp == this_k):
                            countnightshift += 0
                        else:
                            countnightshift += 1
            if(countnightshift >= nightdaylimit[this_i]):
                ans = False
                return ans              
        #第一週
        else:
            countnightshift = 0
            for theday in D_WEEK[0]:
                for tmp in S_NIGHT:
                    if(work[this_i,theday,tmp] == 1):
                        if(theday == this_j and tmp == this_k):
                            countnightshift += 0
                        else:
                            countnightshift += 1
            if(countnightshift+LMNIGHT[this_i] >= nightdaylimit[this_i]):
                ans = False
                return ans            
            
    #排班的上限
    for item in UPPER:
        if(this_i == item[0] and this_j in DAYset[item[1]] and this_k in SHIFTset[item[2]]):
            tmpcount = 0
            for whichday in DAYset[item[1]]:
                for tmp in  SHIFTset[item[2]]:
                    if(work[this_i,whichday,tmp]==1):
                        if(whichday == this_j and tmp == this_k):
                            tmpcount+=0
                        else:
                            tmpcount+=1
            if(tmpcount>=item[3]):
                ans = False
                return ans

    # 若在非ASSIGN情況下不能排AS、MS、O班
    if this_k in SHIFTset['not_assigned']:
        if(assign_par[this_i][this_j][this_k]==0):
            ans = False
            return ans

    
    #排特殊技能班別的上限
    
    #有每月總數上限
    for item in Upper_shift:
        if(this_k in SHIFTset[item[0]]):
            if(this_i in E_SKILL['phone']):
                tmpcount = 0
                for whichday in DAY:
                    if(work[this_i,whichday,this_k]==1):
                        if(whichday == this_j):
                            tmpcount+=0
                        else:
                            tmpcount+=1
                if(tmpcount>=item[1]):
                    ans = False
                    return ans
            else:   #無此技能
                ans = False
                return ans
    
    
    #特殊技能排班
    for item in NOTPHONE_CLASS:
        if(this_k in SHIFTset[item[0]]):
            if(this_i in E_SKILL[item[2]]):
                tmpcount = 0
                for people in EMPLOYEE:
                    if(work[people,this_j,this_k]==1):
                        if(people == this_i):
                            tmpcount+=0
                        else:
                            tmpcount+=1
                if(tmpcount>=item[1]):
                    ans = False
                    return ans
            else:   #無此技能
                ans = False
                return ans

    #特殊技能排班（有假日後要多人的限制）
    for item in NOTPHONE_CLASS_special:
        if(this_k in SHIFTset[item[0]]):
            if(this_i in E_SKILL[item[2]]):
                tmpcount = 0
                for people in EMPLOYEE:
                    if(work[people,this_j,this_k]==1):
                        if(people == this_i):
                            tmpcount+=0
                        else:
                            tmpcount+=1
                            
                if(this_j in VACnextdayset):
                    if(tmpcount>=item[3]):
                        ans = False
                        return ans                  
                else:
                    if(tmpcount>=item[1]):
                        ans = False
                        return ans
            else:   #無此技能
                ans = False
                return ans            

    #無特殊技能者不得排特殊技能班
    for item in SKILL_list:
        if (this_k in SKILLset[item]):
            if (this_i not in E_SKILL[item]):
                ans = False
                return ans

    #年資限制
    if consider == True:
        for i in range(len(PERCENT)):
            item = PERCENT[i]
            if (this_k in SHIFTset[item[1]]):
                if (this_j in DAYset[item[0]]):
                    if (this_i not in E_SENIOR[i]):
                        countS = 0
                        countT = 0
                        for s in E_SENIOR[i]:
                            if work[s,this_j,this_k] == True:
                                countS += 1
                        for t in EMPLOYEE:
                            if work[t,this_j,this_k] == True:
                                countT += 1
                        if (countS/(countT+1) < item[2]):
                            ans = False
                            return ans

    
    return ans                 

def REPEAT(this_i,this_j,this_k):   #一次安排可滿足多條限制式時使用
    ans = False
    
    for k in SHIFT:
        if(work[this_i,this_j,k] == 1) and (k == this_k):    
            ans = True
    return ans                    
#========================================================================#
# GENE(): 切分並交配的函數 
#========================================================================#
def GENE(timelimit, available_sol, fix, generation, per_month_dir=tl.DIR_PER_MONTH, posibility = mutate_prob):
	return gen.gene_alg(timelimit, available_sol, fix, generation, per_month_dir, posibility = posibility)

#========================================================================#
# SHIFT_ORDER(): 班別排序的函數 
#========================================================================#
def takeNeck(alist):
	try:
		return alist[-1]
	except:
		print('找不到項目 ',end='')
		print(alist,end='')
		print(' 的瓶頸程度參數')
		return None
def SHIFT_ORDER(demand, shift, day, sumlack_t, maxsurplus, maxnight, sumbreak_t, maxnoon, csr, arranged):
    ans = []
    for c in csr:
        for a in range(len(day)):
            if arranged[c][day[a]] == True:
                continue
            else:
                for i in shift:
                    if ABLE(c,day[a],i)==False:
                        continue
                    sumlack = copy.deepcopy(sumlack_t)
                    sumbreak = copy.deepcopy(sumbreak_t)
                    maxsurplus_t = copy.deepcopy(maxsurplus)
                    maxnight_t = copy.deepcopy(maxnight)
                    maxnoon_t = copy.deepcopy(maxnoon)
                    demand_t = []
                    demand_t.extend(demand[a])
                    for t in range(nT):
                        if CONTAIN[i][t] == 1:
                            demand_t[t] -=1
                            if demand_t[t] >= 0:
                                sumlack -= 1
                    dem_s = np.array(demand_t)
                    for j in range(len(dem_s)):
                        if dem_s[j] > 0:
                            dem_s[j] = 0
                    if min(dem_s)*(-1) >= maxsurplus:
                        maxsurplus_t += 1

                    if i in S_NIGHT:
                        if nightdaylimit[c] > 0:
                            ni = 0
                            for y in range(nDAY):
                                for z in S_NIGHT:
                                    if work[c,y,z] == True:
                                        ni += 1
                                        break
                            ni = ni / nightdaylimit[c]
                            if ni >= maxnight:
                                maxnight_t += 1
                        else:
                            maxnight_t = 1000000*nEMPLOYEE*nDAY*nT
                    elif i in S_NOON:
                        no = 0
                        for y in range(nDAY):
                            for z in S_NOON:
                                if work[c,y,z] == True:
                                    no += 1
                                    break
                        if no >= maxnoon: 
                            maxnoon_t += 1
                    for w in WEEK:
                        if day[a] in D_WEEK[w]:
                            for br in BREAK:
                                if i in S_BREAK[br]:
                                    if breakCount[c,w,br] == False:
                                        sumbreak += 1
                                    break
                            break    

                    d = P0 * (sumlack+1000000*(sumlack>LACK)*(sumlack-LACK)) + \
                        P1 * (maxsurplus_t+1000000*(maxsurplus_t>SURPLUS)*(maxsurplus_t-SURPLUS)) + \
                        P2 * (maxnight_t+1000000*(maxnight_t>NIGHT)*(maxnight_t-NIGHT)) +\
                        P3 * (sumbreak+1000000*(sumbreak>BREAKCOUNT)*(sumbreak-BREAKCOUNT)) +\
                        P4 * (maxnoon_t+1000000*(maxnoon_t>NOON)*(maxnoon_t-NOON))
                    
                    ans.append([c,day[a],i,d])
    ans.sort(key=takeNeck, reverse=False)
    
    return ans 

def LIMIT_CSR_SHIFT_ORDER(TYPE, demand, shift_list, day, sumlack_t, maxsurplus, maxnight, sumbreak_t, maxnoon, csr_list, skilled):
    ans = []
    for i in csr_list:
        for s in shift_list:
            sumlack = copy.deepcopy(sumlack_t)
            sumbreak = copy.deepcopy(sumbreak_t)
            maxsurplus_t = copy.deepcopy(maxsurplus)
            maxnight_t = copy.deepcopy(maxnight)
            maxnoon_t = copy.deepcopy(maxnoon)
            demand_t = []
            demand_t.extend(demand)
            for t in range(nT):
                if CONTAIN[s][t] == 1:
                    demand_t[t] -=1
                    if demand_t[t] >= 0:
                        sumlack -= 1
            dem_s = np.array(demand_t)
            for j in range(len(dem_s)):
                if dem_s[j] > 0:
                    dem_s[j] = 0
            if min(dem_s)*(-1) >= maxsurplus:
                maxsurplus_t += 1
            
            if s in S_NIGHT:
                if nightdaylimit[i] > 0:
                    ni = 0
                    for y in range(nDAY):
                        for z in S_NIGHT:
                            if work[i,y,z] == True:
                                ni += 1
                                break
                    ni = ni / nightdaylimit[i]
                    if ni >= maxnight:
                        maxnight_t += 1
                else:
                    maxnight_t = 1000000*nEMPLOYEE*nDAY*nT
            elif s in S_NOON:
                no = 0
                for y in range(nDAY):
                    for z in S_NOON:
                        if work[i,y,z] == True:
                            no += 1
                            break
                if no >= maxnoon: 
                    maxnoon_t += 1
            for w in WEEK:
                if day in D_WEEK[w]:
                    for br in BREAK:
                        if s in S_BREAK[br]:
                            if breakCount[i,w,br] == False:
                                sumbreak += 1
                            break
                    break    

            d = P0 * (sumlack+1000000*(sumlack>LACK)*(sumlack-LACK)) + \
                P1 * (maxsurplus_t+1000000*(maxsurplus_t>SURPLUS)*(maxsurplus_t-SURPLUS)) + \
                P2 * (maxnight_t+1000000*(maxnight_t>NIGHT)*(maxnight_t-NIGHT)) +\
                P3 * (sumbreak+1000000*(sumbreak>BREAKCOUNT)*(sumbreak-BREAKCOUNT)) +\
                P4 * (maxnoon_t+1000000*(maxnoon_t>NOON)*(maxnoon_t-NOON))
            
            ans.append([i,s,d])
    ans.sort(key=takeNeck, reverse=False)

    return ans

def SPECIAL_CSR_ORDER(shift, day, maxnight, sumbreak_t, maxnoon, csr_list):
    ans = []
    for i in csr_list:
        sumbreak = copy.deepcopy(sumbreak_t)
        maxnight_t = copy.deepcopy(maxnight)
        maxnoon_t = copy.deepcopy(maxnoon)
        if shift in S_NIGHT:
            if nightdaylimit[i] > 0:
                ni = 0
                for y in range(nDAY):
                    for z in S_NIGHT:
                        if work[i,y,z] == True:
                            ni += 1
                            break
                ni = ni / nightdaylimit[i]
                if ni >= maxnight:
                    maxnight_t += 1
            else:
                maxnight_t = 1000000*nEMPLOYEE*nDAY*nT
        elif shift in S_NOON:
            no = 0
            for y in range(nDAY):
                for z in S_NOON:
                    if work[i,y,z] == True:
                        no += 1
                        break
            if no >= maxnoon: 
                maxnoon_t += 1
        for w in WEEK:
            if day in D_WEEK[w]:
                for br in BREAK:
                    if shift in S_BREAK[br]:
                        if breakCount[i,w,br] == False:
                            sumbreak += 1
                        break
                break 

        d = P2 * (maxnight_t+1000000*(maxnight_t>NIGHT)*(maxnight_t-NIGHT)) +\
            P3 * (sumbreak+1000000*(sumbreak>BREAKCOUNT)*(sumbreak-BREAKCOUNT)) +\
            P4 * (maxnoon_t+1000000*(maxnoon_t>NOON)*(maxnoon_t-NOON))
        
        ans.append([i,d])
    ans.sort(key=takeNeck, reverse=False)
    if shuffle == True:
        rd.shuffle(ans)
   
    return ans

def DAY_ORDER(day, demand_list):
    ans = []
    for i in range(len(day)):
        #sumlack = copy.deepcopy(sumlack_t)
        #maxsurplus_t = copy.maxsurplus
        demand_t = []
        demand_t.extend(demand_list[i])
        dem_l = np.array(demand_t)
        dem_s = np.array(demand_t)
        dem_su = 0
        for j in range(len(dem_l)):
            if dem_l[j] < 0:
                dem_l[j] = 0
        for j in range(len(dem_s)):
            if dem_s[j] > 0:
                dem_s[j] = 0
        if min(dem_s)*(-1) == maxsurplus:
            dem_su = 0
        else:
            dem_su = 1
        d = P0 * np.sum(dem_l) + P1 * (1-dem_su)
        ans.append([day[i],d])
    ans.sort(key=takeNeck, reverse=True)

    return ans 
#=======================================================================================================#
#====================================================================================================#
#=================================================================================================#
#  main function
#=================================================================================================#
#====================================================================================================#
#=======================================================================================================#

LIMIT_MATRIX = LIMIT_ORDER(ordernum, IGNORE) #生成多組限制式matrix
#print(LIMIT_MATRIX)
sequence = 0 #限制式順序
char = 'a' #CSR沒用度順序
fix = [] #存可行解的哪些部分是可以動的


#迴圈計時
tStart = time.time()
#成功數計算
success = 0
#產生100個親代的迴圈
for p in range(parent):
    
    ordercount = (p)%1+1     #每重算一次SHIFT_SET的排序數
    maxnight = 0
    maxnoon = 0
    maxsurplus = 0
    unconfimed = False
    skilled = {}
    for j in DAY:
        for k in SHIFTset['all']:
            skilled[Shift_name[k],j] = []

    #初始缺工人數
    sumlack_t = 0
    for j in range(nDAY):
        for t in range(nT):
            sumlack_t += DEMAND[j][t]    
    #初始午休次數
    sumbreak_t = 0
    
    #動態需工人數
    CURRENT_DEMAND = [tmp for tmp in range(nDAY)]
    for j in DAY:
        CURRENT_DEMAND[j] = []
        for t in range(nT):
            CURRENT_DEMAND[j].append(DEMAND[j][t])
    
    #指定班別
    for c in ASSIGN:
        if ABLE(c[0],c[1],c[2]) == False:
            unconfimed = True
        work[c[0],c[1],c[2]] = True
        for w in WEEK:
            if c[1] in D_WEEK[w]:
                for br in BREAK:
                    if c[2] in S_BREAK[br]:
                        if breakCount[c[0],w,br] == False:
                            breakCount[c[0],w,br] = True
                            sumbreak_t += 1
                        break
                break
        if c[2] in SHIFTset['phone']: #非其他班別時扣除需求
            for t in range(nT):
                if CONTAIN[c[2]][t] == 1:
                    CURRENT_DEMAND[c[1]][t] -= 1
                    if CURRENT_DEMAND[c[1]][t] >= 0:
                        sumlack_t -= 1
            demand = []
            demand.extend(CURRENT_DEMAND[c[1]])
            for q in range(len(demand)):
                if demand[q] > 0:
                    demand[q] = 0
            if min(demand)*(-1) > maxsurplus:
                maxsurplus = min(demand)*(-1)
        if c[2] in S_NIGHT:
            ni = 0
            for j in range(nDAY):
                for k in S_NIGHT:
                    if work[c[0],j,k] == True:
                        ni += 1
                        break
            ni = ni / nightdaylimit[c[0]]
            if ni > maxnight:
                maxnight = ni
        elif c[2] in S_NOON:
            no = 0
            for y in range(nDAY):
                for z in S_NOON:
                    if work[c[0],y,z] == True:
                        no += 1
                        break
            if no > maxnoon:
                maxnoon = no
    
    #瓶頸排班
    LIMIT_LIST = LIMIT_MATRIX[sequence] #一組限制式排序
    LIMIT = [] #一條限制式
    CSR_LIST = [] #可排的員工清單
    BOUND = [] #限制人數
    for l in range(len(LIMIT_LIST)):
        LIMIT = LIMIT_LIST[l]
        nightbound = False
        #print(LIMIT)
        for n in S_NIGHT:
            if LIMIT[3][0] == n:
                nightbound = True
                break
        CSR_LIST = CSR_ORDER(char, LIMIT[0], LIMIT[1], EMPLOYEE_t, Posi, nightbound) #員工沒用度排序
        #rd.shuffle(LIMIT[2])
        demand_list = []
        for m in LIMIT[2]:
            demand_list.append(CURRENT_DEMAND[m])
        DAY_SET = DAY_ORDER(LIMIT[2], demand_list)
        DAY_LIST = []
        for h in range(len(DAY_SET)):
            DAY_LIST.append(DAY_SET[h][0])
        for j in DAY_LIST:
            if LIMIT[0] == 'lower' :
                BOUND = LIMIT[4]
                #for i in CSR_LIST:
                DAY_DEMAND = []
                DAY_DEMAND.extend(CURRENT_DEMAND[j])
                LOWER_SET = LIMIT_CSR_SHIFT_ORDER(LIMIT[0], DAY_DEMAND, LIMIT[3], j, sumlack_t, maxsurplus, maxnight, sumbreak_t, maxnoon, CSR_LIST, skilled)
                
                for x in range(len(LOWER_SET)):
                    if BOUND <= 0:
                        break
                    i = LOWER_SET[x][0]
                    k = LOWER_SET[x][1]
                    if k in SHIFTset['not_assigned']:
                        continue
                    for oth in SKILL:
                        if k == SHIFTset[oth[0]][0]:
                            if skilled[Shift_name[k],j] != []:
                                for sk in skilled[Shift_name[k],j]:
                                    if sk in CSR_LIST:
                                        BOUND -= 1
                            break
                    for oth in SKILL_SPECIAL:
                        if k == SHIFTset[oth[0]][0]:
                            if skilled[Shift_name[k],j] != []:
                                for sk in skilled[Shift_name[k],j]:
                                    if sk in CSR_LIST:
                                        BOUND -= 1
                            break
                    for ra in PERCENT:
                        if j in DAYset[ra[0]]:
                            if k in SHIFTset[ra[1]]:
                                if skilled[Shift_name[k],j] != []:
                                    for sk in skilled[Shift_name[k],j]:
                                        if sk in CSR_LIST:
                                            BOUND -= 1
                    if BOUND <= 0:
                        break
                    if ABLE(i, j, k) == True: #若此人可以排此班，就排
                        repeat = False
                        if REPEAT(i, j, k) == True:
                            repeat = True
                        work[i, j, k] = True
                        for w in WEEK:
                            if j in D_WEEK[w]:
                                for br in BREAK:
                                    if k in S_BREAK[br]:
                                        if breakCount[i,w,br] == False:
                                            breakCount[i,w,br] = True
                                            sumbreak_t += 1
                                        break
                                break
                        if k in SHIFTset['phone'] and repeat == False: #非其他班別時扣除需求
                            for t in range(nT):
                                if CONTAIN[k][t] == 1:              
                                    CURRENT_DEMAND[j][t] -= 1
                                    if CURRENT_DEMAND[j][t] >= 0:
                                        sumlack_t -= 1
                            demand = []
                            demand.extend(CURRENT_DEMAND[j])
                            for q in range(len(demand)):
                                if demand[q] > 0:
                                    demand[q] = 0
                            if min(demand)*(-1) > maxsurplus:
                                maxsurplus = min(demand)*(-1)
                        if k in S_NIGHT:
                            ni = 0
                            for y in range(nDAY):
                                for z in S_NIGHT:
                                    if work[i,y,z] == True:
                                        ni += 1
                                        break
                            ni = ni / nightdaylimit[i]
                            if ni > maxnight:
                                maxnight = ni
                        elif k in S_NOON:
                            no = 0
                            for y in range(nDAY):
                                for z in S_NOON:
                                    if work[i,y,z] == True:
                                        no += 1
                                        break
                            if no > maxnoon:
                                maxnoon = no
                        BOUND -= 1
                        skilled[Shift_name[k],j].append(i)
                    else:
                        continue
                if BOUND > 0:
                    unconfimed = True
                    continue
            elif LIMIT[0] == 'ratio':
                DAY_DEMAND = []
                DAY_DEMAND.extend(CURRENT_DEMAND[j])
                RATIO_SET = LIMIT_CSR_SHIFT_ORDER(LIMIT[0], DAY_DEMAND, LIMIT[3], j, sumlack_t, maxsurplus, maxnight, sumbreak_t, maxnoon, CSR_LIST, skilled)
                rd.shuffle(LIMIT[3])
                for k in LIMIT[3]:
                    BOUND = LIMIT[4]
                    if k in SHIFTset['not_assigned']:
                        continue
                    skill_limit = False
                    for oth in SKILL:
                        if k == SHIFTset[oth[0]][0]:
                            skill_limit = True
                            break
                    for oth in SKILL_SPECIAL:
                        if k == SHIFTset[oth[0]][0]:
                            skill_limit = True
                            break
                    for low in LOWER:
                        if j == low[0]:
                            if k in SHIFTset[low[1]]:
                                if skilled[Shift_name[k],j] != []:
                                    for sk in skilled[Shift_name[k],j]:
                                        if sk in CSR_LIST:
                                            BOUND -= 1
                    if BOUND <= 0:
                        continue
                    if skill_limit == True:
                        continue
                    RATIO_CSR_LIST = []
                    for i in range(len(RATIO_SET)):
                        if RATIO_SET[i][1] == k:
                            RATIO_CSR_LIST.append(RATIO_SET[i][0])
                    for i in RATIO_CSR_LIST:
                        if BOUND <= 0:
                            break
                        elif ABLE(i, j, k) == True: #若此人可以排此班，就排
                            repeat = False
                            if REPEAT(i, j, k) == True:
                                repeat = True
                            work[i, j, k] = True
                            for w in WEEK:
                                if j in D_WEEK[w]:
                                    for br in BREAK:
                                        if k in S_BREAK[br]:
                                            if breakCount[i,w,br] == False:
                                                breakCount[i,w,br] = True
                                                sumbreak_t += 1
                                            break
                                    break
                            if k in SHIFTset['phone'] and repeat == False: #非其他班別時扣除需求
                                for t in range(nT):
                                    if CONTAIN[k][t] == 1:              
                                        CURRENT_DEMAND[j][t] -= 1
                                        if CURRENT_DEMAND[j][t] >= 0:
                                            sumlack_t -= 1
                                demand = []
                                demand.extend(CURRENT_DEMAND[j])
                                for q in range(len(demand)):
                                    if demand[q] > 0:
                                        demand[q] = 0
                                if min(demand)*(-1) > maxsurplus:
                                    maxsurplus = min(demand)*(-1)
                            if k in S_NIGHT:
                                ni = 0
                                for y in range(nDAY):
                                    for z in S_NIGHT:
                                        if work[i,y,z] == True:
                                            ni += 1
                                            break
                                ni = ni / nightdaylimit[i]
                                if ni > maxnight:
                                    maxnight = ni
                            elif k in S_NOON:
                                no = 0
                                for y in range(nDAY):
                                    for z in S_NOON:
                                        if work[i,y,z] == True:
                                            no += 1
                                            break
                                if no > maxnoon:
                                    maxnoon = no
                            BOUND -= 1
                            skilled[Shift_name[k],j].append(i)
                        else:
                            continue
                    if BOUND > 0:
                        unconfimed = True
                        continue
            elif LIMIT[0] == 'skill':
                for k in LIMIT[3]:
                    if k in SHIFTset['not_assigned']:
                        continue
                    BOUND = LIMIT[4]
                    for low in LOWER:
                        if j == low[0]:
                            if k in SHIFTset[low[1]]:
                                if skilled[Shift_name[k],j] != []:
                                    for sk in skilled[Shift_name[k],j]:
                                        if sk in CSR_LIST:
                                            BOUND -= 1
                    for ra in PERCENT:
                        if j in DAYset[ra[0]]:
                            if k in SHIFTset[ra[1]]:
                                if skilled[Shift_name[k],j] != []:
                                    for sk in skilled[Shift_name[k],j]:
                                        if sk in CSR_LIST:
                                            BOUND -= 1
                    if BOUND <= 0:
                        continue
                    SPECIAL_CSR_SET = SPECIAL_CSR_ORDER(k, j, maxnight, sumbreak_t, maxnoon, CSR_LIST)
                    SPECIAL_CSR_LIST = []
                    for i in range(len(SPECIAL_CSR_SET)):
                        SPECIAL_CSR_LIST.append(SPECIAL_CSR_SET[i][0])
                    for i in SPECIAL_CSR_LIST:
                        if BOUND <= 0:
                            break
                        elif ABLE(i, j, k) == True: #若此人可以排此班，就排
                            repeat = False
                            if REPEAT(i, j, k) == True:
                                repeat = True
                            work[i, j, k] = True
                            for w in WEEK:
                                if j in D_WEEK[w]:
                                    for br in BREAK:
                                        if k in S_BREAK[br]:
                                            if breakCount[i,w,br] == False:
                                                breakCount[i,w,br] = True
                                                sumbreak_t += 1
                                            break
                                    break
                            if k in SHIFTset['phone'] and repeat == False: #非其他班別時扣除需求
                                for t in range(nT):
                                    if CONTAIN[k][t] == 1:              
                                        CURRENT_DEMAND[j][t] -= 1
                                        if CURRENT_DEMAND[j][t] >= 0:
                                            sumlack_t -= 1
                                demand = []
                                demand.extend(CURRENT_DEMAND[j])
                                for q in range(len(demand)):
                                    if demand[q] > 0:
                                        demand[q] = 0
                                if min(demand)*(-1) > maxsurplus:
                                    maxsurplus = min(demand)*(-1)
                            if k in S_NIGHT:
                                ni = 0
                                for y in range(nDAY):
                                    for z in S_NIGHT:
                                        if work[i,y,z] == True:
                                            ni += 1
                                            break
                                ni = ni / nightdaylimit[i]
                                if ni > maxnight:
                                    maxnight = ni
                            elif k in S_NOON:
                                no = 0
                                for y in range(nDAY):
                                    for z in S_NOON:
                                        if work[i,y,z] == True:
                                            no += 1
                                            break
                                if no > maxnoon:
                                    maxnoon = no
                            BOUND -= 1
                            skilled[Shift_name[k],j].append(i)
                        else:
                            continue
                    if BOUND > 0:
                        unconfimed = True
                        continue
            elif LIMIT[0] == 'skill_special':
                for k in LIMIT[3]:
                    if k in SHIFTset['not_assigned']:
                        continue
                    BOUND = LIMIT[4]
                    SPECIAL_CSR_SET = SPECIAL_CSR_ORDER(k, j, maxnight, sumbreak_t, maxnoon, CSR_LIST)
                    SPECIAL_CSR_LIST = []
                    for i in range(len(SPECIAL_CSR_SET)):
                        SPECIAL_CSR_LIST.append(SPECIAL_CSR_SET[i][0])
                    for i in SPECIAL_CSR_LIST:
                        if BOUND <= 0:
                            break
                        elif ABLE(i, j, k) == True: #若此人可以排此班，就排
                            repeat = False
                            if REPEAT(i, j, k) == True:
                                repeat = True
                            work[i, j, k] = True
                            for w in WEEK:
                                if j in D_WEEK[w]:
                                    for br in BREAK:
                                        if k in S_BREAK[br]:
                                            if breakCount[i,w,br] == False:
                                                breakCount[i,w,br] = True
                                                sumbreak_t += 1
                                            break
                                    break
                            if k in SHIFTset['phone'] and repeat == False: #非其他班別時扣除需求
                                for t in range(nT):
                                    if CONTAIN[k][t] == 1:              
                                        CURRENT_DEMAND[j][t] -= 1
                                        if CURRENT_DEMAND[j][t] >= 0:
                                            sumlack_t -= 1
                                demand = []
                                demand.extend(CURRENT_DEMAND[j])
                                for q in range(len(demand)):
                                    if demand[q] > 0:
                                        demand[q] = 0
                                if min(demand)*(-1) > maxsurplus:
                                    maxsurplus = min(demand)*(-1)
                            if k in S_NIGHT:
                                ni = 0
                                for y in range(nDAY):
                                    for z in S_NIGHT:
                                        if work[i,y,z] == True:
                                            ni += 1
                                            break
                                ni = ni / nightdaylimit[i]
                                if ni > maxnight:
                                    maxnight = ni
                            elif k in S_NOON:
                                no = 0
                                for y in range(nDAY):
                                    for z in S_NOON:
                                        if work[i,y,z] == True:
                                            no += 1
                                            break
                                if no > maxnoon:
                                    maxnoon = no
                            BOUND -= 1
                            skilled[Shift_name[k],j].append(i)
                        else:
                            continue
                    if BOUND > 0:
                        unconfimed = True
                        continue
    
    sequence += 1
    if sequence >= len(LIMIT_MATRIX) and char == 'a':
        sequence = 0
        char = 'b'
    elif sequence >= len(LIMIT_MATRIX) and char == 'b':
        sequence = 0
        char = 'c'
    elif sequence >= len(LIMIT_MATRIX) and char == 'c':
        sequence = 0
        char = 'd'
    elif sequence >= len(LIMIT_MATRIX) and char == 'd':
        sequence = 0
        char = 'e'
    elif sequence >= len(LIMIT_MATRIX) and char == 'e':
        sequence = 0
        char = 'a'
    
    
    
    #=================================================================================================#
    #安排空班別
    #=================================================================================================#
    fix_temp = []
    arranged = []
    for i in range(nEMPLOYEE):
        employee = []
        arranged_t = []
        for j in range(nDAY):
            employee.append(-1)
            arranged_t.append(False)
        fix_temp.append(employee)
        arranged.append(arranged_t)
    for i in range(nEMPLOYEE):
        for j in range(nDAY):
            for k in range(nK):
                if work[i,j,k] == True:
                    arranged[i][j] = True
                    fix_temp[i][j] = 1
                    break
    if p < cutpoint:
        #print('Loading...')
        #優先排能減少缺工冗員最多的班
        for y in range(nEMPLOYEE*nDAY*nK):
            if unconfimed == True:
                for i in range(nEMPLOYEE):
                    for j in range(nDAY):
                        if arranged[i][j] == False:
                            work[i,j,1] = True
                            for w in WEEK:
                                if j in D_WEEK[w]:
                                    for br in BREAK:
                                        if (1 in S_BREAK[br]):
                                            if breakCount[i,w,br] == False:
                                                breakCount[i,w,br] = True
                                                sumbreak_t += 1
                                            break
                                    break
                            for t in range(nT):
                                if CONTAIN[1][t] == 1:              
                                    CURRENT_DEMAND[j][t] -= 1
                                    if CURRENT_DEMAND[j][t] >= 0:
                                        sumlack_t -= 1
                            arranged[i][j] = True
                            fix_temp[i][j] = 0
                break
            finished = True
            count = 0
            for i in range(nEMPLOYEE):
                for j in range(nDAY):
                    if fix_temp[i][j] == -1:
                        count += 1
                        finished = False
            #print(y, count)
            if count%10==0:
                sys.stdout.write("\rLoading...("+str(int(count/10))+")*")
                sys.stdout.flush()
            if finished == True:
                sys.stdout.write("\n")
                break
            else: 
                DAY_DEMAND = []
                DAY_DEMAND.extend(CURRENT_DEMAND)
                SHIFT_SET = SHIFT_ORDER(DAY_DEMAND, SHIFTset['all'], DAY, sumlack_t, maxsurplus, maxnight, sumbreak_t, maxnoon, EMPLOYEE, arranged)
                order = 0
                #for q in range(10):
                #    print(y, SHIFT_SET[q])
                for x in range(len(SHIFT_SET)):
                    i = SHIFT_SET[x][0]
                    j = SHIFT_SET[x][1]
                    
                    if arranged[i][j] == True:
                        continue
                    else:
                        r = SHIFT_SET[x][2]
                        #print(i, j, r)
                        if ABLE(i,j,r,True) == True and REPEAT(i, j, r) == False:
                            work[i,j,r] = True
                            for w in WEEK:
                                if j in D_WEEK[w]:
                                    for br in BREAK:
                                        if r in S_BREAK[br]:
                                            if breakCount[i,w,br] == False:
                                                breakCount[i,w,br] = True
                                                sumbreak_t += 1
                                            break
                                    break
                            if r in SHIFTset['phone']: #非其他班別時扣除需求
                                for t in range(nT):
                                    if CONTAIN[r][t] == 1:              
                                        CURRENT_DEMAND[j][t] -= 1
                                        if CURRENT_DEMAND[j][t] >= 0:
                                            sumlack_t -= 1
                                demand = []
                                demand.extend(CURRENT_DEMAND[j])
                                for q in range(len(demand)):
                                    if demand[q] > 0:
                                        demand[q] = 0
                                if min(demand)*(-1) > maxsurplus:
                                    maxsurplus = min(demand)*(-1)
                            if r in S_NIGHT:
                                ni = 0
                                for y in range(nDAY):
                                    for z in S_NIGHT:
                                        if work[i,y,z] == True:
                                            ni += 1
                                            break
                                ni = ni / nightdaylimit[i]
                                if ni > maxnight:
                                    maxnight = ni
                            elif r in S_NOON:
                                no = 0
                                for y in range(nDAY):
                                    for z in S_NOON:
                                        if work[i,y,z] == True:
                                            no += 1
                                            break
                                if no > maxnoon:
                                    maxnoon = no
                            arranged[i][j] = True
                            fix_temp[i][j] = 0
                            order += 1
                    if order >= ordercount:
                        break
    else:
        E_LIST = []
        E_LIST.extend(EMPLOYEE)
        rd.shuffle(E_LIST)
        
        for i in E_LIST:
            if unconfimed == True:
                for ii in range(nEMPLOYEE):
                    for j in range(nDAY):
                        if arranged[ii][j] == False:
                            work[ii,j,1] = True
                            for w in WEEK:
                                if j in D_WEEK[w]:
                                    for br in BREAK:
                                        if (1 in S_BREAK[br]):
                                            if breakCount[ii,w,br] == False:
                                                breakCount[ii,w,br] = True
                                                sumbreak_t += 1
                                            break
                                    break
                            for t in range(nT):
                                if CONTAIN[1][t] == 1:              
                                    CURRENT_DEMAND[j][t] -= 1
                                    if CURRENT_DEMAND[j][t] >= 0:
                                        sumlack_t -= 1
                            arranged[ii][j] = True
                            fix_temp[ii][j] = 0
                break
            DAY_SET = DAY_ORDER(DAY, CURRENT_DEMAND)
            DAY_LIST = []
            for h in range(len(DAY_SET)):
                DAY_LIST.append(DAY_SET[h][0])
            #print(i, DAY_LIST)
            for j in DAY_LIST:
                if arranged[i][j] == True:
                    continue
                else:
                    DAY_DEMAND = []
                    DAY_DEMAND.extend(CURRENT_DEMAND[j])
                    SHIFT_SET = SHIFT_ORDER([DAY_DEMAND], SHIFTset['all'], [j], sumlack_t, maxsurplus, maxnight, sumbreak_t, maxnoon, [i], arranged)
                    SHIFT_LIST = []
                    for k in range(len(SHIFT_SET)):
                        SHIFT_LIST.append(SHIFT_SET[k][2])
                    #優先排能減少缺工冗員最多的班
                    for r in SHIFT_LIST:
                        if ABLE(i,j,r,True) == True and REPEAT(i, j, r) == False:
                            work[i,j,r] = True
                            for w in WEEK:
                                if j in D_WEEK[w]:
                                    for br in BREAK:
                                        if r in S_BREAK[br]:
                                            if breakCount[i,w,br] == False:
                                                breakCount[i,w,br] = True
                                                sumbreak_t += 1
                                            break
                                    break
                            if r in SHIFTset['phone']: #非其他班別時扣除需求
                                for t in range(nT):
                                    if CONTAIN[r][t] == 1:              
                                        CURRENT_DEMAND[j][t] -= 1
                                        if CURRENT_DEMAND[j][t] >= 0:
                                            sumlack_t -= 1
                                demand = []
                                demand.extend(CURRENT_DEMAND[j])
                                for q in range(len(demand)):
                                    if demand[q] > 0:
                                        demand[q] = 0
                                if min(demand)*(-1) > maxsurplus:
                                    maxsurplus = min(demand)*(-1)
                            if r in S_NIGHT:
                                ni = 0
                                for y in range(nDAY):
                                    for z in S_NIGHT:
                                        if work[i,y,z] == True:
                                            ni += 1
                                            break
                                ni = ni / nightdaylimit[i]
                                if ni > maxnight:
                                    maxnight = ni
                            elif r in S_NOON:
                                no = 0
                                for y in range(nDAY):
                                    for z in S_NOON:
                                        if work[i,y,z] == True:
                                            no += 1
                                            break
                                if no > maxnoon:
                                    maxnoon = no
                            arranged[i][j] = True
                            fix_temp[i][j] = 0
                            break
    

    #work, fix_temp, CURRENT_DEMAND = ARRANGEMENT(work, nEMPLOYEE, nDAY, nK, CONTAIN, CURRENT_DEMAND, nT)
    fix.append(fix_temp)
    #print(fix)
    #print(sumlack_t, maxsurplus, maxnight, sumbreak_t, maxnoon)
    
    #=================================================================================================#
    #計算變數
    #=================================================================================================#
    surplus_temp = 0
    for j in DAY:
        for t in TIME:
            if CURRENT_DEMAND[j][t] > 0:    
                lack[j, t] = CURRENT_DEMAND[j][t]
            else:
                surplus_temp = -1 * CURRENT_DEMAND[j][t]
                if surplus_temp > surplus:
                    surplus = surplus_temp
    
    nightCount_temp = {}
    for i in EMPLOYEE:
        nightCount_temp[i] = 0
        if (nightdaylimit[i]>0):
            count = 0
            for j in DAY:
                for k in S_NIGHT:
                    if work[i, j, k] == True:
                        count += 1
                        break
            nightCount_temp[i] = count / nightdaylimit[i]  
        if nightCount_temp[i] > nightCount:
            nightCount = nightCount_temp[i]
    """
    for i in EMPLOYEE:
        for w in WEEK:
            for j in D_WEEK[w]:
                for r in BREAK:
                    for k in S_BREAK[r]:
                        if work[i, j, k] == True:
                            breakCount[i,w,r] = True
    """
    noonCount_temp = {}
    for i in EMPLOYEE:
        noonCount_temp[i] = 0
        for j in DAY:
            for k in S_NOON:
                if work[i, j, k] == True:
                    noonCount_temp[i] += 1
                    break
        if noonCount_temp[i] > noonCount:
            noonCount = noonCount_temp[i]
    
    
    #=================================================================================================#
    # 輸出
    #=================================================================================================#
    #Dataframe_x
    K_type = Shift_name
    
    employee_name = E_NAME
    employee_name2 = EMPLOYEE
    which_worktime = []
    which_worktime2 = []
    for i in EMPLOYEE:
        tmp = []
        tmp2 = []
        for j in DAY:
            for k in SHIFT:
                if(work[i,j,k]==True):
                    tmp.append(K_type[k])
                    tmp2.append(k)
                    break
            else:
                print('CSR ',E_NAME[i],' 在',DATES[j],'號的排班發生錯誤。')
                ERROR('請嘗試讓程式運行更多時間，或是減少限制條件。\n')
        which_worktime.append(tmp)
        which_worktime2.append(tmp2)
            
    
    #df_x = pd.DataFrame(which_worktime, index = employee_name, columns = DATES)   #字串班表
    #print(df_x)
    df_list = which_worktime2
    
    #=================================================================================================#
    #確認解是否可行
    #=================================================================================================#
    message = 'All constraints are met.'
    message = confirm(df_list)
        
    
    #====================================================================================================#
    #計算目標式
    #====================================================================================================#
    df_x1 = pd.DataFrame(df_list, index = employee_name, columns = DATES) #整數班表
    #result = score(df_x1)
    
    sumlack = 0
    for j in range(nDAY):
        for t in range(nT):
            sumlack += lack[j, t]
    
    sumbreak = 0
    for i in EMPLOYEE:
        for w in WEEK:
             for r in BREAK:
                if breakCount[i,w,r] == True:
                    sumbreak += 1
    
    result = P0 * sumlack + P1 * surplus + P2 * nightCount + P3 * sumbreak + P4 * noonCount
    #print(result, sumlack, surplus, nightCount, sumbreak, noonCount)
    
    #print("result2 = ", result2)
    for j in range(nDAY):
        for t in range(nT):
            lack[j, t] = 0
    
    surplus = 0
    nightCount = 0

    for i in range(nEMPLOYEE):
        for w in range(nW):
            for r in range(nR):
                breakCount[i, w, r] = False
    
    noonCount = 0
    
    #====================================================================================================#
    #將結果放入INITIAL_POOL中
    #====================================================================================================#
    INITIAL_POOL.append(Pool(result, df_x1))
    
    for i in range(nEMPLOYEE):
        for j in range(nDAY):
            for k in range(nK):
                work[i, j, k] = False
    
    
    if message != 'All constraints are met.':
        INITIAL_POOL[p].result = INITIAL_POOL[p].result * 1000000
    else:
        success += 1

    print('\n生成INITIAL POOL： parent =',p,', result =', INITIAL_POOL[p].result)
    print(message+'\n')
    if message != 'All constraints are met.':
        print('Some constraints fails.\n')
    if INITIAL_POOL[p].result < miniresult:
        miniresult = INITIAL_POOL[p].result
        #minidf = INITIAL_POOL[p].df_x1
    
    if p == parent-1:
        print("\nINITIAL POOL completed")
        
    #====================================================================================================#
    #====================================================================================================#
print('\n產生',parent,'個結果於 initail pool (',success,'個合理解) ，共花費', (time.time()-tStart) ,'秒')
if success <= 0:
    ERROR('無合理解，請檢查限制式是否互相矛盾或限制不合理。')

print("\n親代最佳分數: result = ",miniresult,'\n\n')
#print(score(minidf))

available_sol = []

for i in range(parent):
    available_sol.append(INITIAL_POOL[i].df_x1.values.tolist())


#=======================================================================================================#
#====================================================================================================#
#=================================================================================================#
#  切分並交配
#=================================================================================================#
#====================================================================================================#
#=======================================================================================================#
tstart_gen = time.time()
print('\n基因演算法開始')
print('time limit =',timelimit)
gene_result = GENE(timelimit,available_sol, fix, generation, per_month_dir=tl.DIR_PER_MONTH, posibility = 0.5)


#=======================================================================================================#
#====================================================================================================#
#=================================================================================================#
#  輸出
#=================================================================================================#
#====================================================================================================#
#=======================================================================================================#
print('基因演算法共耗時',time.time()-tstart_gen,'秒\n')
print('基因演算法進行',generation,'代\n')
schedule_t = pd.DataFrame(gene_result, index = employee_name, columns = DATES)
#print(schedule_t)
#schedule.to_csv(EmployeeTest[1:]+'alg_Schedul_2019_4.csv', encoding="utf-8_sig")

#=======================================================================================================#
# 若在非ASSIGN情況下不能排not_assigned班別
#=======================================================================================================#
schedule_list = schedule_t.values.tolist()
        
#============================================================================#
# 輸出
schedule = pd.DataFrame(schedule_list, index = employee_name, columns = DATES)
#print(schedule)
result = tl.OUTPUT(schedule, isALG=True)     #建立一個專門用來輸出的class物件
df, df_lack = result.printAll(makeFile=True)    
""" result.printAll()
    輸出：tuple (班表, 缺工冗員表)
    參數：makefile, makeFile=True會將班表、缺工冗員表另外存成csv，False則只有xlsx檔
"""
print('\n\n\n\n=============== 班表 ===============\n', df)
print('\n\n\n\n============= 缺工冗員表 ============\n', df_lack)

#============================================================================#


#只有score需要的參數
A_t = tl.ClassTime_t           #班別-時段對照表的原始檔案
df_x = result.Schedule

score = final_score(A_t, nEMPLOYEE, nDAY, nW, nK, nT, nR, DEMAND, P0, P1, P2, P3, P4, SHIFTset, WEEK_of_DAY, nightdaylimit, S_BREAK, df_x.values.tolist())

print('score:',score)

print('\n\n*** Done in', time.time()-tstart_0 ,'sec. ***')


