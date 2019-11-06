def AddId(info, db_path):
    file = open(db_path+'wca_id.csv', encoding='utf-8', mode='r')
    print(info)
    info = [info[1][:10], info[0]]
    names=file.readlines()
    for i in names:
        if i[:10] == info[0]:
            return
    file = open(db_path+'wca_id.csv', encoding='utf-8', mode='a')

    file.write(','.join(info)+'\n')
    file.close()