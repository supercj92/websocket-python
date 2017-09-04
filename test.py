import requests

pm_id_products = "49177122-61216043,49178264-61316976,49424758-61205485,50821491-61197808,50997742-61171860,52131277-61172288,52965240-61965110,54643859-64258519"
product_ids = "52965240,54643859,49178264,49424758,50821491,49177122,52131277,50997742"
cms_page_version_id = '566647'
province_id = '2'

pmIdProductList = pm_id_products.split(",")
map = {}
for i in pmIdProductList:
    item = i.split("-")
    map[item[0]] = item[1]

product_list = product_ids.split(",")
pm_list = []
for sin_product in product_list:
    if map.has_key(sin_product):
        pm_list.append(map[sin_product])

pm_str = ",".join(pm_list)
module_cache_key = 'zx_1.0_findProductByPminfoIds_prefix_' + pm_str

page_cache_key = 'mobile_getStoreCms_merchantId_201949versionId_%sprovinceId_%s' % (cms_page_version_id, province_id)

module_url = 'http://shop.yhd.com/v1/tools/tools/clearCache.action?cacheKey=' + module_cache_key
page_url = 'http://shop.yhd.com/v1/tools/tools/clearCache.action?cacheKey=' + page_cache_key
print module_url
print page_url
r1 = requests.get(module_url)
print r1.status_code
r2 = requests.get(page_url)
print r2.status_code


