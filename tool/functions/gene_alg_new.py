import time
import numpy as np
import pandas as pd
import random
import os
import platform

#our file
import tool.tool as tl
from tool.score_new import score
from tool.functions.CONFIRM import confirm
from tool.tool import ERROR

#1.永遠只拿前幾名，抽兩個來交配
#2.用更好的子代取代親代
#3.加入突變（新班表必然突變掉隨機一個班，若成不可行解就一百萬）
#4.在gene中要做confirm，可能可能不用


#K_type = ['O','A2','A3','A4','A5','MS','AS','P2','P3','P4','P5','N1','M1','W6','CD','C2','C3','C4','OB']
#K_type_dict = {0:'O',1:'A2',2:'A3',3:'A4',4:'A5',5:'MS',6:'AS',7:'P2',8:'P3',9:'P4',10:'P5',11:'N1',12:'M1',13:'W6',14:'CD',15:'C2',16:'C3',17:'C4',18:'OB'}

def alg(score_liz, main, nDAY, nEMPLOYEE, shiftset, posibility = 0.05):

    org_len = len(score_liz)
    #sort = sorted(score_liz, key = lambda s: s[2]) #親代排名
    new = np.copy(score_liz[:int(len(score_liz)/3)]) #取出前1/3
    num_list = list(range(len(new)))
    random.shuffle(num_list)
    #print(num_list[0],num_list[1], end=' ')

    union = np.logical_or(new[num_list[0]][1], new[num_list[1]][1])
    one_not_avb = union * new[num_list[0]][0]
    one_avb = new[num_list[0]][0] - one_not_avb
    two_not_avb = union * new[num_list[1]][0]
    two_avb = new[num_list[1]][0] - two_not_avb
    one_org = np.array(new[num_list[0]][0]) #沒有fix的班表
    two_org = np.array(new[num_list[1]][0])

    #隨機決定切分點
    sp_row = random.randint(0,nDAY-1)
    sp_col = random.randint(0,nEMPLOYEE-1)

    #第一組：依據員工、日期切分
    one_col_left = one_avb[:sp_col]
    one_col_right = one_avb[sp_col:]
    one_row_up = one_avb.T[:sp_row].T
    one_row_down = one_avb.T[sp_row:].T
    one_org_col_left = one_org[:sp_col]
    one_org_col_right = one_org[sp_col:]
    one_org_row_up = one_org.T[:sp_row].T
    one_org_row_down = one_org.T[sp_row:].T

    #第二組：的切分
    two_col_left = two_avb[:sp_col]
    two_col_right = two_avb[sp_col:]
    two_row_up = two_avb.T[:sp_row].T
    two_row_down = two_avb.T[sp_row:].T
    two_org_col_left = two_org[:sp_col]
    two_org_col_right = two_org[sp_col:]
    two_org_row_up = two_org.T[:sp_row].T
    two_org_row_down = two_org.T[sp_row:].T
    
    #將對應的一、二組片段重新組合
    #上下黏合
    a_one_one_two = np.concatenate((one_row_up, two_row_down), axis=1) + one_not_avb
    a_two_one_two = np.concatenate((one_row_up, two_row_down), axis=1) + two_not_avb
    a_one_two_one = np.concatenate((two_row_up, one_row_down), axis=1) + one_not_avb
    a_two_two_one = np.concatenate((two_row_up, one_row_down), axis=1) + two_not_avb
    a_org_one_two = np.concatenate((one_org_row_up, two_org_row_down), axis=1)
    a_org_two_one = np.concatenate((two_org_row_up, one_org_row_down), axis=1)

    #左右黏合
    b_one_one_two = np.concatenate((one_col_left, two_col_right), axis=0) + one_not_avb
    b_two_one_two = np.concatenate((one_col_left, two_col_right), axis=0) + two_not_avb
    b_one_two_one = np.concatenate((two_col_left, one_col_right), axis=0) + one_not_avb
    b_two_two_one = np.concatenate((two_col_left, one_col_right), axis=0) + two_not_avb
    b_org_one_two = np.concatenate((one_org_col_left, two_org_col_right), axis=0)
    b_org_two_one = np.concatenate((two_org_col_left, one_org_col_right), axis=0)

    range_num = int(1 / posibility) - 1
    #突變
    if random.randint(0,range_num) == 0:
        a_one_one_two[random.randint(0,a_one_one_two.shape[0]-1)][random.randint(0,a_one_one_two.shape[1]-1)] = random.choice(shiftset)
    if random.randint(0,range_num) == 0:
        a_two_one_two[random.randint(0,a_two_one_two.shape[0]-1)][random.randint(0,a_two_one_two.shape[1]-1)] = random.choice(shiftset)
    if random.randint(0,range_num) == 0:
        a_one_two_one[random.randint(0,a_one_two_one.shape[0]-1)][random.randint(0,a_one_two_one.shape[1]-1)] = random.choice(shiftset)
    if random.randint(0,range_num) == 0:
        a_two_two_one[random.randint(0,a_two_two_one.shape[0]-1)][random.randint(0,a_two_two_one.shape[1]-1)] = random.choice(shiftset)
    if random.randint(0,range_num) == 0:
        a_org_one_two[random.randint(0,a_org_one_two.shape[0]-1)][random.randint(0,a_org_one_two.shape[1]-1)] = random.choice(shiftset)
    if random.randint(0,range_num) == 0:
        a_org_two_one[random.randint(0,a_org_two_one.shape[0]-1)][random.randint(0,a_org_two_one.shape[1]-1)] = random.choice(shiftset)
    if random.randint(0,range_num) == 0:
        b_one_one_two[random.randint(0,b_one_one_two.shape[0]-1)][random.randint(0,b_one_one_two.shape[1]-1)] = random.choice(shiftset)
    if random.randint(0,range_num) == 0:
        b_two_one_two[random.randint(0,b_two_one_two.shape[0]-1)][random.randint(0,b_two_one_two.shape[1]-1)] = random.choice(shiftset)
    if random.randint(0,range_num) == 0:
        b_one_two_one[random.randint(0,b_one_two_one.shape[0]-1)][random.randint(0,b_one_two_one.shape[1]-1)] = random.choice(shiftset)
    if random.randint(0,range_num) == 0:
        b_two_two_one[random.randint(0,b_two_two_one.shape[0]-1)][random.randint(0,b_two_two_one.shape[1]-1)] = random.choice(shiftset)
    if random.randint(0,range_num) == 0:
        b_org_one_two[random.randint(0,b_org_one_two.shape[0]-1)][random.randint(0,b_org_one_two.shape[1]-1)] = random.choice(shiftset)
    if random.randint(0,range_num) == 0:
        b_org_two_one[random.randint(0,b_org_two_one.shape[0]-1)][random.randint(0,b_org_two_one.shape[1]-1)] = random.choice(shiftset)
    
    #print(np.zeros(a_org_one_two.shape))
    #判斷是否符合
    if confirm(a_one_one_two) == 'All constraints are met.':
        #print('a_one_one_two',a_one_one_two)
        score_liz.append((a_one_one_two,new[num_list[0]][1],score(a_one_one_two.tolist(), main)))
        #print(score(a_one_one_two.tolist(), main))
       
    if confirm(a_two_one_two) == 'All constraints are met.':
        #print('a_two_one_two',a_two_one_two)
        score_liz.append((a_two_one_two,new[num_list[1]][1],score(a_two_one_two.tolist(), main)))
        #print(score(a_two_one_two.tolist(), main))
    
    if confirm(a_one_two_one) == 'All constraints are met.':
        #print('a_one_two_one',a_one_two_one)
        score_liz.append((a_one_two_one,new[num_list[0]][1],score(a_one_two_one.tolist(), main)))
        #print(score(a_one_two_one.tolist(), main))
    
    if confirm(a_two_two_one) == 'All constraints are met.':
        #print('a_two_two_one',a_two_two_one)
        score_liz.append((a_two_two_one,new[num_list[1]][1],score(a_two_two_one.tolist(), main)))
        #print(score(a_two_two_one.tolist(), main))
    
    if confirm(a_org_one_two) == 'All constraints are met.':
        #print('a_org_one_two',a_org_one_two)
        score_liz.append((a_org_one_two,np.zeros(a_org_one_two.shape),score(a_org_one_two.tolist(), main)))
        #print(score(a_org_one_two.tolist(), main))
    
    if confirm(a_org_two_one) == 'All constraints are met.':
        #print('a_org_two_one',a_org_two_one)
        score_liz.append((a_org_two_one,np.zeros(a_org_two_one.shape),score(a_org_two_one.tolist(), main)))
        #print(score(a_org_two_one.tolist(), main))
    
    if confirm(b_one_one_two) == 'All constraints are met.':
        #print('b_one_one_two',b_one_one_two)
        score_liz.append((b_one_one_two,new[num_list[0]][1],score(b_one_one_two.tolist(), main)))
        #print(score(b_one_one_two.tolist(), main))
    
    if confirm(b_two_one_two) == 'All constraints are met.':
        #print('b_two_one_two',b_two_one_two)
        score_liz.append((b_two_one_two,new[num_list[1]][1],score(b_two_one_two.tolist(), main)))
        #print(score(b_two_one_two.tolist(), main))
    
    if confirm(b_one_two_one) == 'All constraints are met.':
        #print('b_one_two_one',b_one_two_one)
        score_liz.append((b_one_two_one,new[num_list[0]][1],score(b_one_two_one.tolist(), main)))
        #print(score(b_one_two_one.tolist(), main))
    
    if confirm(b_two_two_one) == 'All constraints are met.':
        #print('b_two_two_one',b_two_two_one)
        score_liz.append((b_two_two_one,new[num_list[1]][1],score(b_two_two_one.tolist(), main)))
        #print(score(b_two_two_one.tolist(), main))

    if confirm(b_org_one_two) == 'All constraints are met.':
        #print('b_org_one_two',b_org_one_two)
        score_liz.append((b_org_one_two,np.zeros(b_org_one_two.shape),score(b_org_one_two.tolist(), main)))
        #print(score(b_org_one_two.tolist(), main))

    if confirm(b_org_two_one) == 'All constraints are met.':
        #print('b_org_two_one',b_org_two_one)
        score_liz.append((b_org_two_one,np.zeros(b_org_two_one.shape),score(b_org_two_one.tolist(), main)))
        #print(score(b_org_two_one.tolist(), main))
             
    # sort = sorted(sort, key = lambda s: s[2],reverse = True)
    #sort = sorted(sort, key = lambda s: s[2])
    score_liz.sort(key = lambda s: s[2])
    #print(len(sort))
    #score_liz = score_liz[:len(score_liz)]
    #print(sort)
    #print(len(sort))
    return score_liz[:org_len]

def gene_alg(timelimit,avaliable_sol,fix,gen,per_month_dir=tl.DIR_PER_MONTH,fixed_dir = tl.DIR_PARA+'fixed/',posibility = 0.05): #avaliavle_sol 可行解列表 fix 不能移動的列表
    if platform.system() == "Linux":
        os.system("g++ -o ./tool/c++/score_linux ./tool/c++/score.cpp")
        main = "./tool/c++/score_linux "
        print("使用的作業系統為：Linux")
    elif platform.system() == "Darwin":
        os.system("g++ -o ./tool/c++/score_mac ./tool/c++/score.cpp")
        main = "./tool/c++/score_mac "
        print("使用的作業系統為：Mac")
    elif platform.system() == "Windows":
        print("使用的作業系統為：Windows")
        os.system("g++ -o ./tool/c++/score.exe ./tool/c++/score.cpp")
        try:
            open('./tool/c++/score.exe','r')
        except FileNotFoundError:
            ERROR('找不到score.exe檔案，請用C++編譯生成一個執行檔。')
        director = str(os.getcwd()).replace("\\","/")
        main = director+"/tool/c++/score.exe "
    A_t = pd.read_csv(fixed_dir + 'fix_class_time.csv', header = 0, index_col = 0)
    EMPLOYEE_t = tl.Employee_t
    
    Shift_name = tl.CLASS_list
    nightdaylimit = EMPLOYEE_t['night_perWeek']

    year  = tl.YEAR
    month = tl.MONTH

    nEMPLOYEE = tl.nE
    nDAY = tl.nD
    nK = tl.nK
    nT = tl.nT
    nR = tl.nR
    nW = tl.nW
    mDAY = tl.mDAY
    DEMAND = tl.DEMAND

    P0, P1, P2, P3, P4 = tl.P

    SHIFTset = tl.K_CLASS_set
    s_break = tl.K_BREAK_set 
    
    DAY = [tmp for tmp in range(nDAY)]              #DAY - 日子集合，J=0,…,nJ-1
    DATES = tl.DATE_list    #所有的日期 - 對照用
    D_WEEK = tl.D_WEEK_set  	#D_WEEK - 第 w 週中所包含的日子集合
    WEEK_of_DAY = tl.WEEK_list #WEEK_of_DAY - 日子j所屬的那一週\

    #1
    A_t_s = ""
    for i in A_t.values.tolist():
        for j in i:
            A_t_s += str(j)
            A_t_s += ","
        A_t_s += "!"
    main += A_t_s
    main += " "

    #2
    Shift_name_s = ""
    for i in Shift_name:
        Shift_name_s += i
        Shift_name_s += ","
    main += Shift_name_s
    main += " "

    #3
    nightdaylimit_s = ""
    for i in nightdaylimit.values.tolist():
        nightdaylimit_s += str(i)
        nightdaylimit_s += ","
    main += nightdaylimit_s
    main += " "

    #4
    year_s = str(year)
    month_s = str(month)
    nEMPLOYEE_s = str(nEMPLOYEE)
    nDAY_s = str(nDAY)
    nK_s = str(nK)
    nT_s = str(nT)
    nR_s = str(nR)
    nW_s = str(nW)
    mDAY_s = str(mDAY)
    
    main += year_s
    main += " "
    main += month_s
    main += " "
    main += nEMPLOYEE_s
    main += " "
    main += nDAY_s
    main += " "
    main += nK_s
    main += " "
    main += nT_s
    main += " "
    main += nR_s
    main += " "
    main += nW_s
    main += " "
    main += mDAY_s
    main += " "

    #13
    DEMAND_s = ""
    for i in DEMAND:
        for j in i:
            DEMAND_s += str(j)
            DEMAND_s += ","
        DEMAND_s += "!"
    main += DEMAND_s
    main += " "
    
    #14
    P0_s = str(P0)
    P1_s = str(P1)
    P2_s = str(P2)
    P3_s = str(P3)
    P4_s = str(P4)

    main += P0_s
    main += " "
    main += P1_s
    main += " "
    main += P2_s
    main += " "
    main += P3_s
    main += " "
    main += P4_s
    main += " "

    #19
    all_s = ""
    morning_s = ""
    noon_s = ""
    night_s = ""
    phone_s = ""
    other_s = ""
    for i in SHIFTset['all']:
        all_s += str(i)
        all_s += ","
    for i in SHIFTset['morning']:
        morning_s += str(i)
        morning_s += ","
    for i in SHIFTset['noon']:
        noon_s += str(i)
        noon_s += ","
    for i in SHIFTset['night']:
        night_s += str(i)
        night_s += ","
    for i in SHIFTset['phone']:
        phone_s += str(i)
        phone_s += ","
    for i in SHIFTset['other']:
        other_s += str(i)
        other_s += ","
    
    main += all_s
    main += " "
    main += morning_s
    main += " "
    main += noon_s
    main += " "
    main += night_s
    main += " "
    main += phone_s
    main += " "
    main += other_s
    main += " "

    #25
    s_break_s = ""
    for i in s_break:
        for j in i:
            s_break_s += str(j)
            s_break_s += ","
        s_break_s += "!"
    
    main += s_break_s
    main += " "
    
    #26
    DAY_s = ""
    for i in DAY:
        DAY_s += str(i)
        DAY_s += ","

    main += DAY_s
    main += " "
    
    #27
    DATES_s = ""
    for i in DATES:
        DATES_s += str(i)
        DATES_s += ","

    main += DATES_s
    main += " "

    #28
    D_WEEK_s = ""
    for i in D_WEEK:
        for j in i:
            D_WEEK_s += str(j)
            D_WEEK_s += ","
        if len(i) == 0:
            D_WEEK_s += ","
        D_WEEK_s += "!"
    main += D_WEEK_s
    main += " "

    #29
    WEEK_of_DAY_s = ""
    for i in WEEK_of_DAY:
        WEEK_of_DAY_s += str(i)
        WEEK_of_DAY_s += ","
    
    main += WEEK_of_DAY_s
    main += " "
    
    #print(main)
    shiftset = []
    shiftset.extend(SHIFTset['phone'])
    for i in SHIFTset['not_assigned']:
        if i in shiftset:
            shiftset.remove(i)

    print('per_month_dir =',per_month_dir)
    i_nb = []
    tStart = time.time()    #紀錄演算法開始的時間
    for p in range(len(avaliable_sol)):
        #i_nb.append(np.vectorize({v: k for k, v in K_type_dict.items()}.get)(np.array(avaliable_sol[p])).tolist())
        i_nb.append(avaliable_sol[p])
        
    score_liz = []
    gene_log = []   
    for i ,j in zip(i_nb,fix):
        score_liz.append((i,j, score(i, main)))
    
    score_liz.sort(key = lambda s: s[2])   
    for i in range(gen):    #重複指定的次數
        if time.time() - tStart > timelimit:    #如果時間已到，就跳出
            print('限制時間已至，於第',i,'世代跳出')
            break
        score_liz = alg(score_liz, main, nDAY, nEMPLOYEE, shiftset, posibility)
        if i % 100 == 0:
            print('第',i+1,'世代最佳分數：',score_liz[0][2], ' Time: ', int(time.time() - tStart),'s')
        gene_log.append([i+1,time.time() - tStart,score_liz[0][2]])
    gene_log = pd.DataFrame(np.array(gene_log),columns=['generation','time','score'])
    gene_log.to_csv('gene_log.csv')
    result = score_liz[0][0]
    print('\n\n基因演算法最佳解：',score_liz[0][2])
    return result
