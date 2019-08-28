import csv

small = True

#File declerations
if (small) :
    file = 'Graphic Novels-Graphic Novel Collection Small.csv'
else :
    file = 'Graphic Novels-Graphic Novel Collection.csv'
nodesFile = 'nodesQuery.txt'
relationshipsFile = 'relationshipsQuery.txt'

bookArray = []

#Read CSV file into an array
with open(file, 'r') as csvFile:
    reader = csv.reader(csvFile, delimiter=';')
    for row in reader:
        bookArray.append(row)

csvFile.close()

#Get indexes of CSV file
indexes = bookArray.pop(0)

#Indexes of all columns used in generator
idI = indexes.index('Graphic Novel')
bookI = indexes.index('Title')
seriesI = indexes.index('Series')
publisherI = indexes.index('Publisher')
pYearI = indexes.index('Date of Purchase') #Add [6:10]

#Relationship variables
bTs = '-[:IN]->' #Book to Series
bTy = '-[:PURCHASED]->' #Book to Year
sTp = '-[:BY]->' #Series to Publisher

#Arrays of all nodes
books = []
series = []
publishers = []
years = []

#Arrays to check if node has already been generated or not
seriesG = []
publishersG = []
yearsG = []

#Single book node generation
for dBook in bookArray:
    #Find indexes of different nodes if they already exist
    if (dBook[seriesI] in seriesG) :
        seriesIndex = dBook[seriesI]
    else :
        seriesIndex = -1

    if (dBook[publisherI] in publishersG) :
        publisherIndex = dBook[publisherI]
    else :
        publisherIndex = -1

    if (dBook[pYearI][6:10] in yearsG) :
        yearIndex = dBook[pYearI]
    else :
        yearIndex = -1

    books.append('(b' + str(len(books)) + ': Book {title:\"' + dBook[bookI] + '\", id:\"' + dBook[idI] + '\"})')

    if (seriesIndex == -1):
        series.append('(s' + str(len(series)) + ': Serie {name:\"' + dBook[seriesI] + '\"})')
        seriesG.append(dBook[seriesI])

    if (publisherIndex == -1):
        publishers.append('(p' + str(len(publishers)) + ': Publisher {name:\"' + dBook[publisherI] + '\"})')
        publishersG.append(dBook[publisherI])

    if (yearIndex == -1):
        years.append('(y' + str(len(years)) + ': Year {year:\"' + dBook[pYearI][6:10] + '\"})')
        yearsG.append(dBook[pYearI][6:10])

with open(nodesFile, 'w') as nf:
    query = 'CREATE '
    #BOOK NODES
    for bn in books :
        query += bn + ','
    #SERIES NODES
    for sn in series :
        query += sn + ','
    #PUBLISHERS NODES
    for pn in publishers :
        query += pn + ','
    #YEAR NODES
    i = 0
    for yn in years :
        query += yn
        if (i < len(years) - 1) :
            query += ','
        else :
            query += ' RETURN *'
        i += 1
    
    nf.write(query)

nf.close()

#Variables for relationships query
rMatch = 'MATCH '
rWhere = 'WHERE '
rCreate = []
rCreateSTP = []

ir = 0
for rBook in bookArray :
    rMatch += '(b' + str(ir) + ': Book), (s' + str(ir) + ': Serie), (y' + str(ir) + ': Year), '
    rWhere += 'b' + str(ir) + '.id = \"' + rBook[idI] + '\" AND s' + str(ir) + '.name = \"' + rBook[seriesI] +  '\" AND y' + str(ir) + '.year = \"' + rBook[pYearI][6:10] + '\" AND '
    rCreate.append('(b' + str(ir) + ')' + bTs + '(s' + str(ir) + ')')
    rCreate.append('(b' + str(ir) + ')' + bTy + '(y' + str(ir) + ')')
    if ([rBook[seriesI], rBook[publisherI]] not in rCreateSTP):
        rCreateSTP.append([rBook[seriesI], rBook[publisherI]])

    ir += 1

ir = 500
for rel in rCreateSTP :
    rMatch += '(s' + str(ir) + ': Serie), (p' + str(ir) + ': Publisher)'
    rWhere += 's' + str(ir) + '.name = \"' + rel[0] + '\" AND p' + str(ir) + '.name = \"' + rel[1] + '\"'
    rCreate.append('(s' + str(ir) + ')' + sTp + '(p' + str(ir) + ')')
                           
    if (ir - 500 < len(rCreateSTP) - 1) :
        rMatch += ', '
        rWhere += ' AND '
    else :
        rMatch += ' '
        rWhere += ' '
    ir += 1

with open(relationshipsFile, 'w') as rf:
    query = rMatch + rWhere + 'CREATE '
    for p in rCreate :
        query += p
        if (rCreate.index(p) < len(rCreate) - 1) :
            query += ', '
        else :
            query += ' RETURN *'

    rf.write(query)

rf.close()
