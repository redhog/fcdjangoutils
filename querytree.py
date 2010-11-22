import re

key_match_1 = re.compile(r'^(\w+)\.')
key_match_2 = re.compile(r'^(\w+)\[(\w+)\]$')
key_match_3 = re.compile(r'^(\w+)\[(\w+)\]\.')
key_match_4 = re.compile(r'^(\w+)\[]$')

class QueryTree(dict):

    def __init__(self, orig=None, prefix=""):

        if orig is None:
            return
        for i in orig:
            if i[0:len(prefix)] == prefix:
                key = i[len(prefix):]
                m1 = key_match_1.match(key)
                m2 = key_match_2.match(key)
                m3 = key_match_3.match(key)
                m4 = key_match_4.match(key)
                if m1:
                    subkey = m1.group(1)
                    if subkey not in self:
                        self[subkey]= QueryTree(orig, prefix + subkey + ".")
                elif m2:
                    subkey = m2.group(1)
                    idx = m2.group(2)
                    if subkey not in self:
                        self[subkey]= QueryTree()
                    subdict = self[subkey]

                    if idx not in subdict:
                        subdict[idx]= orig[i]

                elif m3:
                    subkey = m3.group(1)
                    idx = m3.group(2)
                    if subkey not in self:
                        self[subkey]= QueryTree()
                    subdict = self[subkey]

                    if idx not in subdict:
                        subdict[idx]= QueryTree(orig, prefix + subkey + "[" + idx +"].")

                elif m4:
                    subkey = m4.group(1)
                    if subkey not in self:
                        self[subkey] = orig.getlist(subkey)
                else:
                    self[key] = orig[i]

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError
    
    def __getitem__(self, name):
        if type(name) is int:
            return dict.__getitem__(self, unicode(name))
        return dict.__getitem__(self, name)
    
    @property
    def as_list(self):
        res = [None] * len(self)
        for key, val in self.iteritems():
            res[int(key)] = val
        return res

def main():
    class qdfake(dict):
        def getlist(self, name):
            return [7,2,4]

    res = QueryTree(
        qdfake({
            'foo':'bar',
            'obj.mem1':'v1',
            'obj.mem2':'v2',
            'dict[7]':'v7',
            'dict[9]':'v9',
            'dict[blaj]':'vblaj',
            'comb[0].fld1':'c0f1',
            'comb[0].fld2':'c0f2',
            'comb[1].fld1':'c1f1',
            'comb[1].fld2':'c1f2',
            
            'comb2[0].fld':'c0f',
            'comb2[0].chld[0].fld':'c0c0f',
            'comb2[0].chld[1].fld':'c0c1f',
            
            'comb2[1].fld':'c1f',
            'comb2[1].chld[0].fld':'c1c0f',
            'comb2[1].chld[1].fld':'c1c1f',
            'comb2[1].chld[2].fld':'c1c2f',
            
            'arr[]':7,
            'arr[]':2,
            'arr[]':4,
            }))

    assert(res['foo'] == 'bar')
    assert(res['comb2'][0].fld == 'c0f')
    assert(res['comb2'][0].chld[0]['fld'] == 'c0c0f')
    assert(res.arr[1] == 2)
    assert(res['arr'][0] == 7)
    assert(res.comb.as_list[1].fld1 == 'c1f1')

if __name__ == '__main__':
    main()

