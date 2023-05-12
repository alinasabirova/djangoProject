from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import pandas as pd
from pandas_geojson import to_geojson

coord = []
param = []
def download_data_from_sm(request):
    import supermagApi as sm
    from datetime import datetime
    import time

    start_time = datetime.now()
    # start = '1974-12-12T12:00'
    start = request.GET.get('dt')
    # print(new_coord)

    (status, stations) = sm.SuperMAGGetInventory('alina', start, 60)
    print(len(stations))

    list = []

    for i in range(len(stations)):
        (status, data) = sm.SuperMAGGetData('alina', start, 60, 'ALL', stations[i])
        N_nez = [temp['nez'] for temp in data.N]
        s = stations[i], data.glat.to_string(index=False), data.glon.to_string(index=False), N_nez[0]
        list.append(s)
        coord.append([data.glat.item(), data.glon.item()])
        param.append([data.sza.item()])

    #print(coord)
    #print(param)

    # st = request.GET.get('coord').split(',')
    # new_coord = [float(s) for s in st]
    # kriging(coord, param)

    df = pd.DataFrame(list, columns=['station', 'latitude', 'longitude', 'par'])
    #df.to_csv(f"C:\\Users\\alino\\PycharmProjects\\djangoProject\\static\\dataa.csv", index=False)
    geo_json = to_geojson(df=df, lat='latitude', lon='longitude', properties=['station', 'par'])
    time.sleep(5)
    print(datetime.now() - start_time)
    return JsonResponse(geo_json)

def kriging(request):
    import openturns as ot
    # Input points
    coordinates_train = coord
    # Output points
    precipitation_train = param

    # Fit
    inputDimension = 2

    # basis = ot.ConstantBasisFactory(inputDimension).build()
    # basis = ot.LinearBasisFactory(inputDimension).build()
    # basis = ot.QuadraticBasisFactory(inputDimension).build()
    basis = []

    covarianceModel = ot.SquaredExponential([1.] * inputDimension, [1.0])
    # covarianceModel = ot.MaternModel([1.0] * inputDimension, 1.5)

    # basis = ot.ConstantBasisFactory(inputDimension).build()
    # covarianceModel = ot.SphericalModel(inputDimension)

    # covarianceModel = ot.SquaredExponential([1.0])
    # covarianceModel.setActiveParameter([])

    # thetaInit = 1.0
    # covariance = ot.GeneralizedExponential([thetaInit], 2.0)

    algo = ot.KrigingAlgorithm(coordinates_train, precipitation_train, covarianceModel, basis)
    algo.run()
    result = algo.getResult()
    krigingMetamodel = result.getMetaModel()

    # Predict
    # coordinates = [15.70, 62.53]  # A new latitude/longitude pair
    # precipitation = krigingMetamodel(coordinates)
    st = request.GET.get('coord').split(',')
    new_coord = [float(s) for s in st]

    precipitation = krigingMetamodel(new_coord)


    list = [('Новая точка', st[0], st[1], str(precipitation[0]))]
    df = pd.DataFrame(list, columns=['station', 'latitude', 'longitude', 'par'])
    geo_json = to_geojson(df=df, lat='latitude', lon='longitude', properties=['station', 'par'])

    return JsonResponse(geo_json)

def index(request):
    # if request.GET.get('submit'):
    #     download_data_from_sm(request.GET.get('datetime'))
    return render(request, 'main/index.html')

# /download_data_from_sm?datetime=document.getElementById('datetime')
