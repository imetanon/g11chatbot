from django.http import HttpResponse
from django.conf import settings
from .models import Place, Category, SubCategory, BusinessHour, Province, SubCategoryKeyword
from django.shortcuts import render
from django.db.models import Q
from functools import reduce

import pandas as pd
# import sefr_cut
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import MinMaxScaler
import re
import ast 

# sefr_cut.load_model(engine='ws1000')

# Create your views here.
def index(request):
    df = pd.read_csv(settings.DATASET_ROOT+'/dataset-latest.csv')
    
    categories = df['Main Categories 1'].unique().tolist()
    for category in categories:
        cat = Category.objects.create(name=category)
    
    sub_categories = df['Sub Categories'].unique().tolist()
    for sub_category in sub_categories:
        sub_cat = SubCategory.objects.create(name=sub_category)
        
    province = Province.objects.get(pk=11)
    
    for index, row in df.iterrows():
        print(row['CombinedName'])
        place = Place.objects.create(
            name = row['CombinedName'],
            address1 = row['location'],
            tambon = row['tambon'],
            review_score = row['review_score'] if not pd.isnull(row['review_score']) else 0,
            review_count = row['review_count'] if not pd.isnull(row['review_count']) else 0,
            online_link = row['website'],
            map_link = row['map_link'],
            latitude = row['latitude'],
            longitude = row['logtitude'],
            phone_number = str(row['phone']).replace(" ",""),
            image_url = row['image'],
            province = province
        )
        
        place_category = Category.objects.get(name=row['Main Categories 1'])
        # print(row['Main Categories 1'])
        place.category.add(place_category)
        # print(place.category.all())
        place_sub_category = SubCategory.objects.get(name=row['Sub Categories'])
        place.sub_category.add(place_sub_category)
        
        for idx in range(10,16):
            if not pd.isnull(row[idx]):
                if not SubCategory.objects.filter(name=row[idx]).exists():
                    print(row[idx])
                    sub_cat = SubCategory.objects.create(name=row[idx],sub_category_type=1)
                    place.sub_category.add(sub_cat)
        
        for idx in range(27,34):
            # print(row[idx])
            time = row[idx]
            open_time = None
            close_time = None
            day = idx - 27
            
            if time == "ปิดทำการ":
                print(f"{df.columns.tolist()[idx]} - ปิดทำการ")
            elif pd.isnull(time):
                print(f"{df.columns.tolist()[idx]} - ไม่พบข้อมูล")
            elif time == "เปิด 24 ชั่วโมง":
                open_time = "00:00"
                close_time = "00:00"
            else:
                # print(repr(time))
                time = str(time).split('–')
                print(time)
                if len(time) >= 2:
                    open_time = time[0]
                    close_time = time[1]
                    print(f"{df.columns.tolist()[idx]} | {time[0]} - {time[1]}")
                    
            business_hour = BusinessHour.objects.create(place=place, day=day, open_time=open_time, close_time=close_time)
        print('========')
    return HttpResponse("Index")

def province(request):
    province_list = [
        { "PROVINCE_ID": 1, "PROVINCE_CODE": "10", "PROVINCE_NAME": "กรุงเทพมหานคร", "GEO_ID": 2 },
        { "PROVINCE_ID": 2, "PROVINCE_CODE": "11", "PROVINCE_NAME": "สมุทรปราการ", "GEO_ID": 2 },
        { "PROVINCE_ID": 3, "PROVINCE_CODE": "12", "PROVINCE_NAME": "นนทบุรี", "GEO_ID": 2 },
        { "PROVINCE_ID": 4, "PROVINCE_CODE": "13", "PROVINCE_NAME": "ปทุมธานี", "GEO_ID": 2 },
        { "PROVINCE_ID": 5, "PROVINCE_CODE": "14", "PROVINCE_NAME": "พระนครศรีอยุธยา", "GEO_ID": 2 },
        { "PROVINCE_ID": 6, "PROVINCE_CODE": "15", "PROVINCE_NAME": "อ่างทอง", "GEO_ID": 2 },
        { "PROVINCE_ID": 7, "PROVINCE_CODE": "16", "PROVINCE_NAME": "ลพบุรี", "GEO_ID": 2 },
        { "PROVINCE_ID": 8, "PROVINCE_CODE": "17", "PROVINCE_NAME": "สิงห์บุรี", "GEO_ID": 2 },
        { "PROVINCE_ID": 9, "PROVINCE_CODE": "18", "PROVINCE_NAME": "ชัยนาท", "GEO_ID": 2 },
        { "PROVINCE_ID": 10, "PROVINCE_CODE": "19", "PROVINCE_NAME": "สระบุรี", "GEO_ID": 2 },
        { "PROVINCE_ID": 11, "PROVINCE_CODE": "20", "PROVINCE_NAME": "ชลบุรี", "GEO_ID": 5 },
        { "PROVINCE_ID": 12, "PROVINCE_CODE": "21", "PROVINCE_NAME": "ระยอง", "GEO_ID": 5 },
        { "PROVINCE_ID": 13, "PROVINCE_CODE": "22", "PROVINCE_NAME": "จันทบุรี", "GEO_ID": 5 },
        { "PROVINCE_ID": 14, "PROVINCE_CODE": "23", "PROVINCE_NAME": "ตราด", "GEO_ID": 5 },
        { "PROVINCE_ID": 15, "PROVINCE_CODE": "24", "PROVINCE_NAME": "ฉะเชิงเทรา", "GEO_ID": 5 },
        { "PROVINCE_ID": 16, "PROVINCE_CODE": "25", "PROVINCE_NAME": "ปราจีนบุรี", "GEO_ID": 5 },
        { "PROVINCE_ID": 17, "PROVINCE_CODE": "26", "PROVINCE_NAME": "นครนายก", "GEO_ID": 2 },
        { "PROVINCE_ID": 18, "PROVINCE_CODE": "27", "PROVINCE_NAME": "สระแก้ว", "GEO_ID": 5 },
        { "PROVINCE_ID": 19, "PROVINCE_CODE": "30", "PROVINCE_NAME": "นครราชสีมา", "GEO_ID": 3 },
        { "PROVINCE_ID": 20, "PROVINCE_CODE": "31", "PROVINCE_NAME": "บุรีรัมย์", "GEO_ID": 3 },
        { "PROVINCE_ID": 21, "PROVINCE_CODE": "32", "PROVINCE_NAME": "สุรินทร์", "GEO_ID": 3 },
        { "PROVINCE_ID": 22, "PROVINCE_CODE": "33", "PROVINCE_NAME": "ศรีสะเกษ", "GEO_ID": 3 },
        { "PROVINCE_ID": 23, "PROVINCE_CODE": "34", "PROVINCE_NAME": "อุบลราชธานี", "GEO_ID": 3 },
        { "PROVINCE_ID": 24, "PROVINCE_CODE": "35", "PROVINCE_NAME": "ยโสธร", "GEO_ID": 3 },
        { "PROVINCE_ID": 25, "PROVINCE_CODE": "36", "PROVINCE_NAME": "ชัยภูมิ", "GEO_ID": 3 },
        { "PROVINCE_ID": 26, "PROVINCE_CODE": "37", "PROVINCE_NAME": "อำนาจเจริญ", "GEO_ID": 3 },
        { "PROVINCE_ID": 27, "PROVINCE_CODE": "39", "PROVINCE_NAME": "หนองบัวลำภู", "GEO_ID": 3 },
        { "PROVINCE_ID": 28, "PROVINCE_CODE": "40", "PROVINCE_NAME": "ขอนแก่น", "GEO_ID": 3 },
        { "PROVINCE_ID": 29, "PROVINCE_CODE": "41", "PROVINCE_NAME": "อุดรธานี", "GEO_ID": 3 },
        { "PROVINCE_ID": 30, "PROVINCE_CODE": "42", "PROVINCE_NAME": "เลย", "GEO_ID": 3 },
        { "PROVINCE_ID": 31, "PROVINCE_CODE": "43", "PROVINCE_NAME": "หนองคาย", "GEO_ID": 3 },
        { "PROVINCE_ID": 32, "PROVINCE_CODE": "44", "PROVINCE_NAME": "มหาสารคาม", "GEO_ID": 3 },
        { "PROVINCE_ID": 33, "PROVINCE_CODE": "45", "PROVINCE_NAME": "ร้อยเอ็ด", "GEO_ID": 3 },
        { "PROVINCE_ID": 34, "PROVINCE_CODE": "46", "PROVINCE_NAME": "กาฬสินธุ์", "GEO_ID": 3 },
        { "PROVINCE_ID": 35, "PROVINCE_CODE": "47", "PROVINCE_NAME": "สกลนคร", "GEO_ID": 3 },
        { "PROVINCE_ID": 36, "PROVINCE_CODE": "48", "PROVINCE_NAME": "นครพนม", "GEO_ID": 3 },
        { "PROVINCE_ID": 37, "PROVINCE_CODE": "49", "PROVINCE_NAME": "มุกดาหาร", "GEO_ID": 3 },
        { "PROVINCE_ID": 38, "PROVINCE_CODE": "50", "PROVINCE_NAME": "เชียงใหม่", "GEO_ID": 1 },
        { "PROVINCE_ID": 39, "PROVINCE_CODE": "51", "PROVINCE_NAME": "ลำพูน", "GEO_ID": 1 },
        { "PROVINCE_ID": 40, "PROVINCE_CODE": "52", "PROVINCE_NAME": "ลำปาง", "GEO_ID": 1 },
        { "PROVINCE_ID": 41, "PROVINCE_CODE": "53", "PROVINCE_NAME": "อุตรดิตถ์", "GEO_ID": 1 },
        { "PROVINCE_ID": 42, "PROVINCE_CODE": "54", "PROVINCE_NAME": "แพร่", "GEO_ID": 1 },
        { "PROVINCE_ID": 43, "PROVINCE_CODE": "55", "PROVINCE_NAME": "น่าน", "GEO_ID": 1 },
        { "PROVINCE_ID": 44, "PROVINCE_CODE": "56", "PROVINCE_NAME": "พะเยา", "GEO_ID": 1 },
        { "PROVINCE_ID": 45, "PROVINCE_CODE": "57", "PROVINCE_NAME": "เชียงราย", "GEO_ID": 1 },
        { "PROVINCE_ID": 46, "PROVINCE_CODE": "58", "PROVINCE_NAME": "แม่ฮ่องสอน", "GEO_ID": 1 },
        { "PROVINCE_ID": 47, "PROVINCE_CODE": "60", "PROVINCE_NAME": "นครสวรรค์", "GEO_ID": 2 },
        { "PROVINCE_ID": 48, "PROVINCE_CODE": "61", "PROVINCE_NAME": "อุทัยธานี", "GEO_ID": 2 },
        { "PROVINCE_ID": 49, "PROVINCE_CODE": "62", "PROVINCE_NAME": "กำแพงเพชร", "GEO_ID": 2 },
        { "PROVINCE_ID": 50, "PROVINCE_CODE": "63", "PROVINCE_NAME": "ตาก", "GEO_ID": 4 },
        { "PROVINCE_ID": 51, "PROVINCE_CODE": "64", "PROVINCE_NAME": "สุโขทัย", "GEO_ID": 2 },
        { "PROVINCE_ID": 52, "PROVINCE_CODE": "65", "PROVINCE_NAME": "พิษณุโลก", "GEO_ID": 2 },
        { "PROVINCE_ID": 53, "PROVINCE_CODE": "66", "PROVINCE_NAME": "พิจิตร", "GEO_ID": 2 },
        { "PROVINCE_ID": 54, "PROVINCE_CODE": "67", "PROVINCE_NAME": "เพชรบูรณ์", "GEO_ID": 2 },
        { "PROVINCE_ID": 55, "PROVINCE_CODE": "70", "PROVINCE_NAME": "ราชบุรี", "GEO_ID": 4 },
        { "PROVINCE_ID": 56, "PROVINCE_CODE": "71", "PROVINCE_NAME": "กาญจนบุรี", "GEO_ID": 4 },
        { "PROVINCE_ID": 57, "PROVINCE_CODE": "72", "PROVINCE_NAME": "สุพรรณบุรี", "GEO_ID": 2 },
        { "PROVINCE_ID": 58, "PROVINCE_CODE": "73", "PROVINCE_NAME": "นครปฐม", "GEO_ID": 2 },
        { "PROVINCE_ID": 59, "PROVINCE_CODE": "74", "PROVINCE_NAME": "สมุทรสาคร", "GEO_ID": 2 },
        { "PROVINCE_ID": 60, "PROVINCE_CODE": "75", "PROVINCE_NAME": "สมุทรสงคราม", "GEO_ID": 2 },
        { "PROVINCE_ID": 61, "PROVINCE_CODE": "76", "PROVINCE_NAME": "เพชรบุรี", "GEO_ID": 4 },
        { "PROVINCE_ID": 62, "PROVINCE_CODE": "77", "PROVINCE_NAME": "ประจวบคีรีขันธ์", "GEO_ID": 4 },
        { "PROVINCE_ID": 63, "PROVINCE_CODE": "80", "PROVINCE_NAME": "นครศรีธรรมราช", "GEO_ID": 6 },
        { "PROVINCE_ID": 64, "PROVINCE_CODE": "81", "PROVINCE_NAME": "กระบี่", "GEO_ID": 6 },
        { "PROVINCE_ID": 65, "PROVINCE_CODE": "82", "PROVINCE_NAME": "พังงา", "GEO_ID": 6 },
        { "PROVINCE_ID": 66, "PROVINCE_CODE": "83", "PROVINCE_NAME": "ภูเก็ต", "GEO_ID": 6 },
        { "PROVINCE_ID": 67, "PROVINCE_CODE": "84", "PROVINCE_NAME": "สุราษฎร์ธานี", "GEO_ID": 6 },
        { "PROVINCE_ID": 68, "PROVINCE_CODE": "85", "PROVINCE_NAME": "ระนอง", "GEO_ID": 6 },
        { "PROVINCE_ID": 69, "PROVINCE_CODE": "86", "PROVINCE_NAME": "ชุมพร", "GEO_ID": 6 },
        { "PROVINCE_ID": 70, "PROVINCE_CODE": "90", "PROVINCE_NAME": "สงขลา", "GEO_ID": 6 },
        { "PROVINCE_ID": 71, "PROVINCE_CODE": "91", "PROVINCE_NAME": "สตูล", "GEO_ID": 6 },
        { "PROVINCE_ID": 72, "PROVINCE_CODE": "92", "PROVINCE_NAME": "ตรัง", "GEO_ID": 6 },
        { "PROVINCE_ID": 73, "PROVINCE_CODE": "93", "PROVINCE_NAME": "พัทลุง", "GEO_ID": 6 },
        { "PROVINCE_ID": 74, "PROVINCE_CODE": "94", "PROVINCE_NAME": "ปัตตานี", "GEO_ID": 6 },
        { "PROVINCE_ID": 75, "PROVINCE_CODE": "95", "PROVINCE_NAME": "ยะลา", "GEO_ID": 6 },
        { "PROVINCE_ID": 76, "PROVINCE_CODE": "96", "PROVINCE_NAME": "นราธิวาส", "GEO_ID": 6 },
        { "PROVINCE_ID": 77, "PROVINCE_CODE": "97", "PROVINCE_NAME": "บึงกาฬ", "GEO_ID": 3 }
    ]
    
    for prov in province_list:
        province = Province.objects.create(code=prov['PROVINCE_CODE'], name=prov['PROVINCE_NAME'])
        print(f"{province.id} - {prov['PROVINCE_NAME']}")

    return HttpResponse("Province")

def possible_word(request):
    df = pd.read_csv(settings.DATASET_ROOT+'/keywords-dataset.csv')
    
    for index, row in df.iterrows():
        keyword_list = ast.literal_eval(row['new_list']) 
        keyword = ', '.join([str(elem) for elem in keyword_list]) 
        if not Category.objects.filter(name=row['main_cat']).exists():
            print(row['main_cat'])
        else:
            sub_cat = SubCategory.objects.filter(name=row['sub_cat'])
            if not sub_cat.exists():
                print(row['sub_cat'])
                if row['sub_cat'] == 'ร้านในตำนาน':
                    sub_cat = SubCategory.objects.get(name='ร้านอาหารในตำนาน')
                    SubCategoryKeyword.objects.update_or_create(sub_category=sub_cat, keyword=keyword)
                elif row['sub_cat'] == 'ร้านอาหาร วิวชายหาด / ชายทะเล':
                    sub_cat = SubCategory.objects.get(name='ร้านอาหารวิวชายหาด / ชายทะเล')
                    SubCategoryKeyword.objects.update_or_create(sub_category=sub_cat, keyword=keyword)
            else:
                SubCategoryKeyword.objects.update_or_create(sub_category=sub_cat[0], keyword=keyword)
    
    
    test_list = SubCategoryKeyword.objects.filter(reduce(lambda x, y: x | y, [Q(keyword__contains=word) for word in ['ซีฟู้ด','ชมวิว','shots']]))
    print(test_list)

    return HttpResponse("Possible Word")