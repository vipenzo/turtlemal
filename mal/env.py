# Environment

class Env():
    def __init__(self, outer=None, binds=None, exprs=None):
        self.data = {}
        self.outer = outer or None

        if binds:
            for i in range(len(binds)):
                if binds[i] == "&":
                    self.data[binds[i+1]] = exprs[i:]
                    break
                else:
                    self.data[binds[i]] = exprs[i]

    def find(self, key):
        if key in self.data: return self
        elif self.outer:     return self.outer.find(key)
        else:                return None

    def set(self, key, value):
        self.data[key] = value
        return value

    def get(self, key):
        env = self.find(key)
        if not env: 
            self.dump()
            raise Exception("'" + key + "' not found")
        return env.data[key]

    def dump(self, indent=""):
        print(f"{indent} env dump {len(self.data)}")
        for key, value in self.data.items():
            print(f"{indent} - {key}={value}")
        if self.outer:
            self.outer.dump(indent+"  ")
            
    def dump_last(self):
        print(f"env dump last {len(self.data)}")
        for key, value in self.data.items():
            print(f" - {key}={value}")
