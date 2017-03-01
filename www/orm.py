import asyncio
import logging;logging.basicConfig(level=logging.INFO)
import aiomysql
import asyncio

async def create_pool(loop,**kw):
    logging.info('create database connection pool...')
    global __pool
    __pool = await aiomysql.create_pool(
        host = kw.get('host','localhost'),
        port = kw.get('port',3306),
        user = kw['user'],
        password=kw['password'],
        db=kw['db'],
        charset = kw.get('charset','utf8'),
        autocommit = kw.get('autocommit',True),
        maxsize = kw.get('maxsize',10),
        minsize=kw.get('minsize',1),
        loop=loop
    )

async def select(sql,args,size=None):
    logging.info(sql,args)
    global __pool
    with (await __pool) as conn:
        cur = await conn.cursor(aiomysql.DictCursor)
        await cur.execute(sql.replace('?','%s'),args or {})
        if size:
            rs = await cur.fetchmany(size)
        else:
            rs = await cur.fetchall()
        await cur.close()
        logging.info('rows returned: %s' % len(rs))
        return rs

async def execute (sql, args):
    logging.info(sql,args)
    with (await __pool) as conn:
        try:
            cur = await conn.cursor()
            await cur.execute(sql.replace('?','%s'), args)
            affected = cur.rowcount
            await cur.close()
        except BaseException as e:
            raise
        return affected

class Field(object):
    def __init__(self,name,colum_type,primary_key,default):
        self.name = name
        self.colum_type = colum_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return ('<%s, %s: %s>' % (self.__class__.__name__, self.colum_type, self.name))

class StringField(Field):

    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)

class IntegerField(Field):

    def __init__(self,name=None, primary_key=False, default=None, ddl='INT(16)'):
        super().__init__(name,ddl,primary_key,default)

class ModelMetaclass(type):

    def __new__(cls,name,bases,attrs):
        if name =='Model':
            return super().__new__(cls,name,bases,attrs)
        tableName = attrs.get('__table__',None) or name
        logging.info('found model: %s(table:%s' % (name,tableName) )
        mappings = dict()
        fields = []
        primaryKey = []
        for k,v in attrs.items():
            if isinstance(v,Field):
                logging.info('  found mapping: %s ==> %s' % (k,v))
                mappings[k] =v
                if v.primary_key:
                    primaryKey.append(k)
                else:
                    fields.append(k)
        primaryKey = tuple(primaryKey)
        if not primaryKey:
            raise RuntimeError('Primary key not found.')
        for k in mappings.keys():
            attrs.pop(k)
        escaped_fields = list(map(lambda  f:'`%s`' %f,fields))
        attrs['__mappings__'] = mappings
        attrs['__table__'] = tableName
        attrs['__primary_key__'] = primaryKey
        attrs['__fields__'] = fields
        attrs['__select__'] = 'SELECT `%s`, %s from `%s' % ('`,`'.join(primaryKey),','.join(escaped_fields),tableName)
        attrs['__insert__'] = 'INSERT INTO `%s` {%s, `%s`} values {%s)' % tableName, ','.join(escaped_fields), '`,`'.join()
        attrs['__update__'] = 'UPDATE `%s` set %s WHERE `%s`' % (tableName, ','.join(map(lambda  f:'`%s`=?' % (mappings.get(f).name or f), fields)), '`=?,`'.join(primaryKey))
        attrs['__delete__'] = 'DELETE FROM %s WHERE `%s`' % (tableName, '`=?,`'.join(primaryKey))
        return type.__new__(cls,name,bases,attrs)

class Model(dict , metaclass=ModelMetaclass):

    def __init__(self, **kwargs):
        super(Model,self).__init__(**kwargs)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % item)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue (self, key):
        return getattr(self,key,None)

    def getValueOrDefault(self, key):
        value = getattr(self,key,None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s: %s' % (key,str(value)))
                setattr(self,key,value)
        return value

    @classmethod
    async def find(cls,pk):
        ' find object by primary key. '
        rs = await select('%s where `%s`' % (cls.__select__, '`=?,`'.join(cls.__primary_key__)),pk,1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    async def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.extend(map(self.getValueOrDefault,self.__primary_key__))
        rows = await execute(self.__insert__,args)
        if rows != 1:
            logging.warning('failed to insert record.')

    @classmethod
    async def findAll(cls,cond):
        conditions = [' 1=1 '].extend(['%s = %s ' % (cls.__mappings__[x].name or x, y) for x,y in cond.iterItems() if x in cls.__mappings__.keys()])
        """这里有SQL注入问题，后期研究API后解决"""
        rs = await select( cls.__select__ + ' WHERE  ' + ' AND '.join(conditions))
        if len(rs) == 0:
            return None
        return [cls(**x) for x in rs]
        pass

    @classmethod
    async def findNumber(cls, cond):
        conditions = [' 1=1 '].extend(['%s = %s ' % (cls.__mappings__[x].name or x, y) for x,y in cond.iterItems() if x in cls.__mappings__.keys()])
        rs = await select('SELECT COUNT(*) FROM %s WHEER %s' % (cls.__table__ , ' AND '.join(conditions)))
        return rs[0] if rs else 0

    async def remove(self):
        conditions = [' 1 = 1 '].extend([' %s = %s ' % (x, self[x]) for x in self.__primary_key__])
        rs = await execute('DELETE FROM %s WHERE %s' % (self.__table__, ' AND '.join(conditions)))
        pass

    async def dbUpdate(self):
        pass


class User(Model):

    __table__ = 'users'

    id = IntegerField(primary_key=True)
    name = StringField()


'''测试代码'''
async def mainTest():
    loop = asyncio.get_event_loop()
    await create_pool(loop,{
        'host' : 'liguangyumysql.cf8iw2auduon.ap-southeast-1.rds.amazonaws.com',
        'port' :  3306,
        'user' : 'gyli',
        'password' : 'gyligyli',
        'db' : 'db',
        'loop' : loop
    })


if __name__ == '__main__':
    pass
