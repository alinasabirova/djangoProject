from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse


def download_data_from_sm(request):
    import supermag as sm
    import pandas as pd
    from pandas_geojson import to_geojson
    # start = [2012, 10, 15, 11, 00, 00]
    start = request.GET.get('dt')
    # print(new_coord)

    (status, stations) = sm.SuperMAGGetInventory('alina', start, 60)
    print(len(stations))

    list = []
    coord = []
    param = []

    for i in range(len(stations)):
        (status, data) = sm.SuperMAGGetData('alina', start, 60, 'ALL', stations[i])
        s = stations[i], data.glat.to_string(index=False), data.glon.to_string(index=False), data.sza.to_string(
            index=False)
        list.append(s)
        ll = [data.glat.item(), data.glon.item()]
        coord.append(ll)
        p = [data.sza.item()]
        param.append(p)

    #print(coord)
    #print(param)

    st = request.GET.get('coord').split(',')
    new_coord = [float(s) for s in st]
    kriging(coord, param, new_coord)

    df = pd.DataFrame(list, columns=['station', 'latitude', 'longitude', 'SZA'])
    #df.to_csv(f"C:\\Users\\alino\\PycharmProjects\\djangoProject\\static\\dataa.csv", index=False)
    geo_json = to_geojson(df=df, lat='latitude', lon='longitude', properties=['station', 'SZA'])

    return JsonResponse(geo_json)

def kriging(coord, param, new_coord):
    import openturns as ot
    # Input points
    coordinates_train = coord
    # Output points
    precipitation_train = param

    # Fit
    inputDimension = 2

    basis = ot.ConstantBasisFactory(inputDimension).build()
    covarianceModel = ot.SquaredExponential([1.] * inputDimension, [1.0])

    algo = ot.KrigingAlgorithm(coordinates_train, precipitation_train, covarianceModel, basis)
    algo.run()
    result = algo.getResult()
    krigingMetamodel = result.getMetaModel()

    # Predict
    # coordinates = [15.70, 62.53]  # A new latitude/longitude pair
    # precipitation = krigingMetamodel(coordinates)
    precipitation = krigingMetamodel(new_coord)
    print(precipitation)
    return (precipitation)

def index(request):
    # if request.GET.get('submit'):
    #     download_data_from_sm(request.GET.get('datetime'))
    return render(request, 'main/index.html')

# /download_data_from_sm?datetime=document.getElementById('datetime')
