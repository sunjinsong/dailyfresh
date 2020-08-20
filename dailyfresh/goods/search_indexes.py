from haystack import indexes
from .models import GoodsSKU

#文件是固定的
#指定对某个类的某些数据建立索引
#建立的格式
class GoodsSKUIndex(indexes.SearchIndex,indexes.Indexable):
    #索引的字段  user_template=True指定根据那些字段建立索引  这些说明放在一个文件中
    text=indexes.CharField(document=True,use_template=True)

    def get_model(self):
        #返回你的模型类
        return GoodsSKU

    #建立索引数据
    def index_queryset(self, using=None):
        return self.get_model().objects.all()