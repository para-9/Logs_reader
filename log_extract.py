with open('Future_Generali_Failed_Proposal_Log.log') as f:
    lines = f.readlines()
    for l in lines:
        if 'SOAP service response' in l:
            print(l)
    c = 0

with open('Future_Generali_Failed_Proposal_Log.log') as f:
    lines = f.readlines()
    for line in lines:
        c +=1
        if 'SOAP-ENV:Envelope xmlns:SOAP-ENV' in line:
            print(line)
            print(lines[c])
            print(lines[c+1])
