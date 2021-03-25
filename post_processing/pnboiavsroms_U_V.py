import pandas as pd
from matplotlib import dates
import numpy as np
from utils import weim


def vel_conv(vel,dir):
  if dir <= 90:
    u = vel*np.sin(np.radians(dir))
    v = vel*np.cos(np.radians(dir))
  if dir > 90 and dir <=180:
    dir=dir-90
    u = vel*np.cos(np.radians(dir))
    v = -vel*np.sin(np.radians(dir))
  if dir > 180 and dir <=270:
    dir=dir-180
    u = -vel*np.sin(np.radians(dir))
    v = -vel*np.cos(np.radians(dir))
  if dir > 270 and dir <=360:
    dir=dir-270
    u = -vel*np.cos(np.radians(dir))
    v = vel*np.sin(np.radians(dir))
  return(u,v)  
  
###############adcp

#adcphis=pd.read_csv('historico_itajai.txt')
#adcphis=pd.read_csv('historico_santos.txt')
adcphis=pd.read_csv('historico_vitoria.txt')
adcphis[adcphis.Lat<-100]=np.nan
adcphis = adcphis.dropna()
lat=adcphis['Lat'].min()
lon=adcphis['Lon'].min()

#adcp=pd.read_csv('adcptratados_itajai.csv')
#adcp=pd.read_csv('adcptratados_santos.csv')
adcp=pd.read_csv('adcptratados_vitoria_2.csv')
adcp[adcp.Cdir3>360]=np.nan
adcp = adcp.dropna()
adcp.reset_index(inplace=True)
adcp['Lat']=lat
adcp['Lon']=lon
adcp['datas']=dates.datestr2num(adcp.data)

vel, dir='Cvel3','Cdir3'
#vel, dir='Cvel14','Cdir14'
#vel, dir='Cvel20','Cdir20'



vel=adcp[vel]
dir=adcp[dir]

u=np.zeros(adcp.shape[0])
v=np.zeros(adcp.shape[0])

for i in range(adcp.shape[0]):
  u[i],v[i] = vel_conv(vel[i], dir[i])
  u[i]=u[i]/1000
  v[i]=v[i]/1000

adcp['umed']=u
adcp['vmed']=v

#########################


from vgrid import s_coordinate, s_coordinate_2, s_coordinate_4
from netCDF4 import Dataset 
from scipy.interpolate import griddata, interp1d
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.pylab import *
from matplotlib import dates
from mpl_toolkits.axes_grid1 import make_axes_locatable
import glob
import xarray as xr

#lista = sorted(glob.glob('R:/Modelos/BRSE_2014_2016/RESULTADOS/ocean_BRSE_his_b1_00[8-9][0-9]*')) + sorted(glob.glob('R:/Modelos/BRSE_2014_2016/RESULTADOS/ocean_BRSE_his_b1_01[0-4][0-9]*'))

#lista = sorted(glob.glob('R:/Modelos/BRSE_2014_2016/RESULTADOS/ocean_BRSE_his_b22_00[1-9][0-9]*')) + sorted(glob.glob('R:/Modelos/BRSE_2014_2016/RESULTADOS/ocean_BRSE_his_b3_00[0-4][0-9]*'))
lista = sorted(glob.glob('/mnt/share/Modelos/BRSE_2014_2016/RESULTADOS/ocean_BRSE_his_b1_04[0-9][0-9]*')) + sorted(glob.glob('/mnt/share/Modelos/BRSE_2014_2016/RESULTADOS/ocean_BRSE_his_b22_00[1-9][0-9]*')) + sorted(glob.glob('/mnt/share/Modelos/BRSE_2014_2016/RESULTADOS/ocean_BRSE_his_b3_00[0-4][0-9]*')) +  sorted(glob.glob('/mnt/share/Modelos/BRSE_2014_2016/RESULTADOS/ocean_BRSE_his_b4_00[0-3][0-9]*'))

#lista = sorted(glob.glob('ocean_BRSE_his_b1_0216.nc'))

#lista = sorted(glob.glob('R:/Modelos/BRSE_2014_2016/RESULTADOS/ocean_BRSE_his_b1_0[3-4][0-9][0-9]*'))

#lista = sorted(glob.glob('R:/Modelos/BRSE_2014_2016/RESULTADOS/ocean_BRSE_his_b1_0[0-9][0-9][0-9]*'))

avgfile = xr.open_mfdataset(lista, concat_dim='ocean_time')
#avgfile = xr.open_mfdataset(lista, concat_dim='ocean_time', decode_cf=False)


hh=np.array(avgfile['ocean_time'][:].dt.strftime('%Y-%m-%d  %H:00:00'))

hhdates=dates.datestr2num(hh)

fname_grd = 'BRSE_2012_GRD.nc'     #CF 1/36

tlst=list(np.arange(0,hh.shape[0],12))

## Load ROMS grid.
grd = Dataset(fname_grd)
x_roms = grd.variables['lon_rho'][:]
y_roms = grd.variables['lat_rho'][:]
msk_roms = grd.variables['mask_rho'][:]
msk_romsv = grd.variables['mask_v'][:]
h_roms = grd.variables['h'][:]
sh2 = msk_roms.shape
etamax, ximax = sh2

x_roms=x_roms[1:-1,1:-1]
y_roms=y_roms[1:-1,1:-1]


ltlatlon=abs(y_roms - lat)
lglatlon=abs(x_roms - lon)
latlon=ltlatlon + lglatlon
ltmin=int(np.where(latlon == latlon.min())[0])
lgmin=int(np.where(latlon == latlon.min())[1])

theta_b = 0.4
theta_s = 5.0
tcline = 3.
klevels = 30
Vtransform = 1
Vstretching = 1
Spherical = True

lst=list(np.arange(0,30))

if Vstretching==4:
  scoord = s_coordinate_4(h_roms, theta_b, theta_s, tcline, klevels)   #zeta is not used in the computation 
elif Vstretching==2:
  scoord = s_coordinate_2(h_roms, theta_b, theta_s, tcline, klevels)
elif Vstretching==1:
  scoord = s_coordinate(h_roms, theta_b, theta_s, tcline, klevels)

zr = -scoord.z_r[:]

zr=zr[lst,1:-1,1:-1] 

zc=np.array([12.5])
#zc=np.array([51])
#zc=np.array([72.])


zc=zc[::-1]


latv=np.array(avgfile['lat_v'][:])
lonv=np.array(avgfile['lon_v'][:])
lonu=np.array(avgfile['lon_u'][:])
latu=np.array(avgfile['lat_u'][:])

uavg=np.array(avgfile.u.isel(s_rho=lst).isel(ocean_time=tlst).values)


uavg = 0.5*(uavg[:,:,:,1:]+uavg[:,:,:,:-1])
lonu = 0.5*(lonu[:,1:]+lonu[:,:-1])
latu = 0.5*(latu[:,1:]+latu[:,:-1])


uavg=uavg[:,:,1:-1,:]
lonu=lonu[1:-1,:]
latu=latu[1:-1,:]

##np.array(avgfile.u.isel(s_rho=lst).isel(ocean_time=[1,2]).values)

vavg=np.array(avgfile.v.isel(s_rho=lst).isel(ocean_time=tlst).values)

vavg = 0.5*(vavg[:,:,1:,:]+vavg[:,:,:-1,:])
latv = 0.5*(latv[1:,:]+latv[:-1,:])
lonv = 0.5*(lonv[1:,:]+lonv[:-1,:])

vavg=vavg[:,:,:,1:-1]
lonv=lonv[:,1:-1]
latv=latv[:,1:-1]


#tempavg=np.array(avgfile.temp.isel(s_rho=lst).isel(ocean_time=tlst).values)
#tempavg=tempavg[:,:,1:-1,1:-1]

ktl=3

uavg=uavg[:,:,ltmin-ktl:ltmin+ktl, lgmin-ktl:lgmin+ktl]
vavg=vavg[:,:,ltmin-ktl:ltmin+ktl, lgmin-ktl:lgmin+ktl]
#tempavg=tempavg[:,:,ltmin-ktl:ltmin+ktl, lgmin-ktl:lgmin+ktl]
x_roms=x_roms[ltmin-ktl:ltmin+ktl, lgmin-ktl:lgmin+ktl]
y_roms=y_roms[ltmin-ktl:ltmin+ktl, lgmin-ktl:lgmin+ktl]


intu=np.zeros([uavg.shape[0],len(zc),x_roms.shape[0], x_roms.shape[1]])

intv=np.zeros([uavg.shape[0],len(zc),x_roms.shape[0], x_roms.shape[1]])

itemp=np.zeros([uavg.shape[0],len(zc),x_roms.shape[0], x_roms.shape[1]])

#zeta=avgfile['zeta'][:]

for j in range(intu.shape[2]):
  for k in range(intu.shape[3]):
    if (zr[-1,j,k] > zc.min()):
      zr[-1,j,k] = zc.min()

zr=zr[:,ltmin-ktl:ltmin+ktl, lgmin-ktl:lgmin+ktl]

UNDEF=np.nan

for i in range(intu.shape[0]):
  for j in range(intu.shape[2]):
    for k in range(intu.shape[3]):
      intu[i,:,j,k] = np.interp(-zc, -zr[:,j,k], uavg[i,:,j,k], right=UNDEF, left=UNDEF)
      intv[i,:,j,k] = np.interp(-zc, -zr[:,j,k], vavg[i,:,j,k], right=UNDEF, left=UNDEF)
#      itemp[i,:,j,k] = np.interp(-zc, -zr[:,j,k], tempavg[i,:,j,k], right=UNDEF, left=UNDEF)

intu=np.squeeze(intu)
intv=np.squeeze(intv)
itemp=np.squeeze(itemp)


romstime=hhdates[tlst]

########adcp

ff=np.where(  (adcp['datas'] > romstime.min()) & (adcp['datas'] < romstime.max()) )

newadcp=adcp.loc[ff]

timeostia=newadcp['datas']

############################################################

intunewtime=np.zeros([len(timeostia),x_roms.shape[0], x_roms.shape[1]])

intvnewtime=np.zeros([len(timeostia),x_roms.shape[0], x_roms.shape[1]])

tempnewtime=np.zeros([len(timeostia),x_roms.shape[0], x_roms.shape[1]])


for j in range(intu.shape[1]):
  for k in range(intu.shape[2]):
    intunewtime[:,j,k] = np.interp(timeostia, romstime, intu[:,j,k], right=UNDEF, left=UNDEF)
    intvnewtime[:,j,k] = np.interp(timeostia, romstime, intv[:,j,k], right=UNDEF, left=UNDEF)
    tempnewtime[:,j,k] = np.interp(timeostia, romstime, itemp[:,j,k], right=UNDEF, left=UNDEF)

intunewtime[intunewtime>100]=np.nan
#plt.pcolor(x_roms, y_roms,np.ma.masked_invalid(intunewtime[-1,:]));plt.show()

vsitu=np.zeros([len(timeostia)])
usitu=np.zeros([len(timeostia)])

for i in range(len(vsitu)):
  vsitu[i]=griddata((x_roms.ravel(),y_roms.ravel()), intvnewtime[i,:].ravel(), (lon,lat))
  usitu[i]=griddata((x_roms.ravel(),y_roms.ravel()), intunewtime[i,:].ravel(), (lon,lat))


vmed=newadcp['vmed']

umed=newadcp['umed']

timevec=newadcp['datas'].values

vbeca=vsitu.copy()
ubeca=usitu.copy()

vson=vsitu.copy()
uson=usitu.copy()


ini=5.5
iii=0
for i in range(20):
  idxpn,deppnb=i+1, ini
  ini=ini+3.5
  print(idxpn,deppnb)
  iii=iii+1
  print('Cvel'+str(idxpn))

vecdep=np.zeros([20])
pu=np.zeros([20])
pv=np.zeros([20])
rmseu=np.zeros([20])
rmsev=np.zeros([20])
ini=5.5
for ii in range(20):
  ###############adcp
  idxpn,vecdep[ii]=ii+1, ini
  #adcphis=pd.read_csv('historico_itajai.txt')
  #adcphis=pd.read_csv('historico_santos.txt')
  adcphis=pd.read_csv('historico_vitoria.txt')
  adcphis[adcphis.Lat<-100]=np.nan
  adcphis = adcphis.dropna()
  lat=adcphis['Lat'].min()
  lon=adcphis['Lon'].min()
  #adcp=pd.read_csv('adcptratados_itajai.csv')
  #adcp=pd.read_csv('adcptratados_santos.csv')
  adcp=pd.read_csv('adcptratados_vitoria_2.csv')
  adcp[adcp.Cdir3>360]=np.nan
  adcp = adcp.dropna()
  adcp.reset_index(inplace=True)
  adcp['Lat']=lat
  adcp['Lon']=lon
  adcp['datas']=dates.datestr2num(adcp.data)
  vel, dir='Cvel'+str(idxpn),'Cdir'+str(idxpn)
  vel=adcp[vel]
  dir=adcp[dir]
  u=np.zeros(adcp.shape[0])
  v=np.zeros(adcp.shape[0])
  for i in range(adcp.shape[0]):
    u[i],v[i] = vel_conv(vel[i], dir[i])
    u[i]=u[i]/1000
    v[i]=v[i]/1000
    
  adcp['umed']=u
  adcp['vmed']=v
  zc=np.array([vecdep[ii]])
  intu=np.zeros([uavg.shape[0],len(zc),x_roms.shape[0], x_roms.shape[1]])
  intv=np.zeros([uavg.shape[0],len(zc),x_roms.shape[0], x_roms.shape[1]])
  itemp=np.zeros([uavg.shape[0],len(zc),x_roms.shape[0], x_roms.shape[1]])
  UNDEF=np.nan
  for i in range(intu.shape[0]):
    for j in range(intu.shape[2]):
      for k in range(intu.shape[3]):
        intu[i,:,j,k] = np.interp(-zc, -zr[:,j,k], uavg[i,:,j,k], right=UNDEF, left=UNDEF)
        intv[i,:,j,k] = np.interp(-zc, -zr[:,j,k], vavg[i,:,j,k], right=UNDEF, left=UNDEF)
        
  intu=np.squeeze(intu)
  intv=np.squeeze(intv)
  ff=np.where(  (adcp['datas'] > romstime.min()) & (adcp['datas'] < romstime.max()) )
  newadcp=adcp.loc[ff]
  timeostia=newadcp['datas']
  ############################################################
  intunewtime=np.zeros([len(timeostia),x_roms.shape[0], x_roms.shape[1]])
  intvnewtime=np.zeros([len(timeostia),x_roms.shape[0], x_roms.shape[1]])
  tempnewtime=np.zeros([len(timeostia),x_roms.shape[0], x_roms.shape[1]])
  for j in range(intu.shape[1]):
    for k in range(intu.shape[2]):
      intunewtime[:,j,k] = np.interp(timeostia, romstime, intu[:,j,k], right=UNDEF, left=UNDEF)
      intvnewtime[:,j,k] = np.interp(timeostia, romstime, intv[:,j,k], right=UNDEF, left=UNDEF)
     
  intunewtime[intunewtime>100]=np.nan
  vsitu=np.zeros([len(timeostia)])
  usitu=np.zeros([len(timeostia)])
  for i in range(len(vsitu)):
    vsitu[i]=griddata((x_roms.ravel(),y_roms.ravel()), intvnewtime[i,:].ravel(), (lon,lat))
    usitu[i]=griddata((x_roms.ravel(),y_roms.ravel()), intunewtime[i,:].ravel(), (lon,lat))
    
  vmed=newadcp['vmed']
  umed=newadcp['umed']
  timevec=newadcp['datas'].values
  vbeca=vsitu.copy()
  ubeca=usitu.copy()
  vmedt=weim(vmed,81)
  umedt=weim(umed,81)
  vsitutdad=weim(vbeca,11)
  usitutdad=weim(ubeca,11)
  pv[ii]=stats.pearsonr(vmedt,vsitutdad)[0]
  rmsev[ii]=np.sqrt(mse(vmedt,vsitutdad))
  pu[ii]=stats.pearsonr(umedt,usitutdad)[0]
  rmseu[ii]=np.sqrt(mse(umedt,usitutdad))
  ini=ini+3.5

    
fig, ax1 = plt.subplots(figsize=(5,7))                 
ax1.plot(pv*100, -vecdep,marker='o', markersize=8, linewidth=2, color='black', label='Componente V')
marker_style = dict(color='tab:red',marker='o',
                    markersize=8, markerfacecoloralt='tab:red')                
ax1.errorbar(pu*100, -vecdep, **marker_style,  linewidth=2, label='Componente U')
ax1.set_xlim([60,90])
ax1.set_ylim([-90,-4])
ax1.set_xlabel('Coeficiente de Pearson (%)', fontsize=14)
ax1.set_ylabel('Profundidade (m)',fontsize=14)
#ax1.set_xticks([-20,0,20])
ax1.grid(alpha=0.5)
#legend=ax1.legend( fontsize='small', loc='lower center', ncol=2)
legend=ax1.legend(loc=3, fancybox=True, framealpha=1, shadow=True, borderpad=1, fontsize='small')
legend.get_frame().set_facecolor('white')
ax1.tick_params(labelsize=12)
plt.savefig('pearson.png', dpi=200, bbox_inches='tight', linestyle='.', transparent=False)
d = {'V': pv*100, 'U': pu*100}
d=pd.DataFrame(d)
d.set_index(vecdep, inplace=True)
d=d.round(2)
d.to_excel('pearson.xlsx') 
#########################


    
fig, ax1 = plt.subplots(figsize=(5,7))                 
ax1.plot(rmsev, -vecdep,marker='o', markersize=8, linewidth=2, color='black', label='Componente V')
marker_style = dict(color='tab:red',marker='o',
                    markersize=8, markerfacecoloralt='tab:red')                
ax1.errorbar(rmseu, -vecdep, **marker_style,  linewidth=2, label='Componente U')
ax1.set_xlim([0,0.35])
ax1.set_ylim([-90,-4])
ax1.set_xlabel('RMSE (m/s)', fontsize=14)
ax1.set_ylabel('Profundidade (m)',fontsize=14)
ax1.set_xticks([0,0.1,0.2,0.3])
ax1.grid(alpha=0.5)
#legend=ax1.legend( fontsize='small', loc='lower center', ncol=2)
legend=ax1.legend(loc=3, fancybox=True, framealpha=1, shadow=True, borderpad=1, fontsize='small')
legend.get_frame().set_facecolor('white')
ax1.tick_params(labelsize=12)
plt.savefig('rmse.png', dpi=200, bbox_inches='tight', linestyle='.', transparent=False)
d = {'V': rmsev, 'U': rmseu}
d=pd.DataFrame(d)
d.set_index(vecdep, inplace=True)
d=d.round(2)
d.to_excel('rmse.xlsx') 
#########################




#######################################################################  MERCATOR

from vgrid import s_coordinate, s_coordinate_2, s_coordinate_4
from netCDF4 import Dataset 
from scipy.interpolate import griddata, interp1d
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.pylab import *
from matplotlib import dates
from mpl_toolkits.axes_grid1 import make_axes_locatable
       

#avgfile=Dataset('HIS_FILE_20200421_5D0-20200428_5D0_hind_correct_year_WEAK_menor_azul_nopline_0005.nc') ##Vitoria 4,5

lista = sorted(glob.glob('HIS_FILE_rotate_4_SUL_2_3_2_NEST_grid2_lp_all_small_ultra_smaler_000[3-4]*'))

avgfile = xr.open_mfdataset(lista, concat_dim='ocean_time')

hh=np.array(avgfile['ocean_time'][:].dt.strftime('%Y-%m-%d  %H:00:00'))

hhdates=dates.datestr2num(hh)


fname_grd = 'rotate_cf_16_09_2.nc'


romstime=hhdates

timeini=dates.num2date(romstime[0]  - 1).strftime("%Y%m%d")
timeend=dates.num2date(romstime[-1]).strftime("%Y%m%d")

input_path='/home/fernando/roms/src/Projects/hindcast_2/mercator/MYOCEAN_AZUL_FORECAST_'    #
#input_path='/home/fernando/roms/src/Projects/hindcast/mercator/MYOCEAN_AZUL_FORECAST_'    #


a=[timeini, timeend]

numdays= np.diff(dates.datestr2num(a)) + 2

n_time=int(numdays[0])

a = dates.datestr2num(a)

time_vec = np.arange(numdays) + a[0]

romstimer=romstime.copy()

romstime=time_vec.copy()


rt=0
file=Dataset(input_path + dates.num2date( time_vec[rt]).strftime("%Y%m%d")+'.nc')
ut=file['uo'][:]

uavg=np.zeros([int(numdays)] + list(np.squeeze(ut).shape))
vavg=np.zeros([int(numdays)] + list(np.squeeze(ut).shape))


for rt in range(int(numdays)):
  #load HYCOM DATA
  nc_hycom=input_path + dates.num2date( time_vec[rt]).strftime("%Y%m%d")+'.nc'
  file=Dataset(nc_hycom)
  uavg[rt,:]=np.squeeze(file['uo'][:])
  vavg[rt,:]=np.squeeze(file['vo'][:])

uavg[uavg<-100]=np.nan
vavg[vavg<-100]=np.nan
zr = file['depth'][:]

zc=np.array([12.5])

#zc=np.array([47.5])

#zc=np.array([51.0])

#zc=np.array([44])

#zc=np.array([72.])



x_fm=file['longitude'][:]
y_fm=file['latitude'][:]
x_fm,y_fm=np.meshgrid(x_fm,y_fm)

minlon = x_fm[0,:] - lon
iml = np.where(np.absolute(minlon)==np.absolute(minlon).min())[0][0]
maxlon = x_fm[0,:] - lon
imxl = np.where(np.absolute(maxlon)==np.absolute(maxlon).min())[0][0]

minlat = y_fm[:,0] - lat
imla = np.where(np.absolute(minlat)==np.absolute(minlat).min())[0][0]
maxlat = y_fm[:,0] - lat
imxla = np.where(np.absolute(maxlat)==np.absolute(maxlat).min())[0][0]

lim=3

uavg=uavg[:,:,imxla-lim:imla+lim,iml-lim:imxl+lim]
vavg=vavg[:,:,imxla-lim:imla+lim,iml-lim:imxl+lim]
tempavg=tempavg[:,:imxla-lim:imla+lim,iml-lim:imxl+lim]


x_fm = x_fm[imxla-lim:imla+lim,iml-lim:imxl+lim]

y_fm = y_fm[imxla-lim:imla+lim,iml-lim:imxl+lim]


intu=np.zeros([uavg.shape[0],len(zc),uavg.shape[2], uavg.shape[3]])

intv=np.zeros([uavg.shape[0],len(zc),uavg.shape[2], uavg.shape[3]])

itemp=np.zeros([uavg.shape[0],len(zc),uavg.shape[2], uavg.shape[3]])

UNDEF=np.nan

for i in range(intu.shape[0]):
  for j in range(intu.shape[2]):
    for k in range(intu.shape[3]):
      intu[i,:,j,k] = np.interp(zc, zr, uavg[i,:,j,k], right=UNDEF, left=UNDEF)
      intv[i,:,j,k] = np.interp(zc, zr, vavg[i,:,j,k], right=UNDEF, left=UNDEF)
#      itemp[i,:,j,k] = np.interp(zc, zr, tempavg[i,:,j,k], right=UNDEF, left=UNDEF)

intu=np.squeeze(intu)
intv=np.squeeze(intv)
itemp=np.squeeze(itemp)


import pandas as pd
from matplotlib import dates
import numpy as np

def vel_conv(vel,dir):
  if dir <= 90:
    u = vel*np.sin(np.radians(dir))
    v = vel*np.cos(np.radians(dir))
  if dir > 90 and dir <=180:
    dir=dir-90
    u = vel*np.cos(np.radians(dir))
    v = -vel*np.sin(np.radians(dir))
  if dir > 180 and dir <=270:
    dir=dir-180
    u = -vel*np.sin(np.radians(dir))
    v = -vel*np.cos(np.radians(dir))
  if dir > 270 and dir <=360:
    dir=dir-270
    u = -vel*np.cos(np.radians(dir))
    v = vel*np.sin(np.radians(dir))
  return(u,v)  
  
###############adcp

#adcphis=pd.read_csv('historico_itajai.txt')
#adcphis=pd.read_csv('historico_vitoria.txt')
adcphis=pd.read_csv('historico_cabofrio.txt')
adcphis[adcphis.Lat<-100]=np.nan
adcphis = adcphis.dropna()
lat=adcphis['Lat'].min()
lon=adcphis['Lon'].min()

#adcp=pd.read_csv('adcptratados_itajai.csv')
#adcp=pd.read_csv('adcptratados_vitoria_2.csv')
adcp=pd.read_csv('adcptratados_cabofrio2.csv')
adcp['Lat']=lat
adcp['Lon']=lon
adcp['datas']=dates.datestr2num(adcp.data)

vel, dir='Cvel3','Cdir3'
#vel, dir='Cvel12','Cdir12'
#vel, dir='Cvel14','Cdir14'
#vel, dir='Cvel9','Cdir9'
#vel, dir='Cvel20','Cdir20'

vel=adcp[vel]
dir=adcp[dir]

u=np.zeros(adcp.shape[0])
v=np.zeros(adcp.shape[0])

for i in range(adcp.shape[0]):
  u[i],v[i] = vel_conv(vel[i], dir[i])
  u[i]=u[i]/1000
  v[i]=v[i]/1000

adcp['umed']=u
adcp['vmed']=v


ff=np.where(  (adcp['datas'] > romstimer.min()) & (adcp['datas'] < romstimer.max()) )

newadcp=adcp.loc[ff]

timeostia=newadcp['datas']

############################################################

intunewtimer=np.zeros([len(romstimer),intu.shape[1], intu.shape[2]])

intvnewtimer=np.zeros([len(romstimer),intu.shape[1], intu.shape[2]])

itempnewtimer=np.zeros([len(romstimer),intu.shape[1], intu.shape[2]])


for j in range(intu.shape[1]):
  for k in range(intu.shape[2]):
    intunewtimer[:,j,k] = np.interp(romstimer, romstime, intu[:,j,k], right=UNDEF, left=UNDEF)
    intvnewtimer[:,j,k] = np.interp(romstimer, romstime, intv[:,j,k], right=UNDEF, left=UNDEF)
    itempnewtimer[:,j,k] = np.interp(romstimer, romstime, itemp[:,j,k], right=UNDEF, left=UNDEF)


intunewtime=np.zeros([len(timeostia),intu.shape[1], intu.shape[2]])

intvnewtime=np.zeros([len(timeostia),intu.shape[1], intu.shape[2]])

tempnewtime=np.zeros([len(timeostia),intu.shape[1], intu.shape[2]])


for j in range(intu.shape[1]):
  for k in range(intu.shape[2]):
    intunewtime[:,j,k] = np.interp(timeostia, romstimer, intunewtimer[:,j,k], right=UNDEF, left=UNDEF)
    intvnewtime[:,j,k] = np.interp(timeostia, romstimer, intvnewtimer[:,j,k], right=UNDEF, left=UNDEF)
    tempnewtime[:,j,k] = np.interp(timeostia, romstimer, itempnewtimer[:,j,k], right=UNDEF, left=UNDEF)

intunewtime[intunewtime>100]=np.nan

#plt.pcolor(np.ma.masked_invalid(intunewtime[-1,:]));plt.show()

vsitu=np.zeros([len(timeostia)])
usitu=np.zeros([len(timeostia)])


for i in range(len(vsitu)):
  vsitu[i]=griddata((x_fm.ravel(),y_fm.ravel()), intvnewtime[i,:].ravel(), (lon,lat))
  usitu[i]=griddata((x_fm.ravel(),y_fm.ravel()), intunewtime[i,:].ravel(), (lon,lat))


vmed=newadcp['vmed']

umed=newadcp['umed']

timevec=newadcp['datas'].values

from utils import weim




vmedt=weim(vmed,61)
vsitut=weim(vsitu,61)
umedt=weim(umed,61)
usitut=weim(usitu,61)


vsitutdad=weim(vbeca,61)
usitutdad=weim(ubeca,61)



vsitutnest=weim(vson, 61)
usitutnest=weim(uson, 61)


vmedt=weim(vmed,81)
umedt=weim(umed,81)
vsitut=weim(vsitu,31)
usitut=weim(usitu,31)
vsitutdad=weim(vbeca,61)
usitutdad=weim(ubeca,61)
vsitutnest=weim(vson, 61)
usitutnest=weim(uson, 61)


umedt=weim(umed,81)
usitut=weim(usitu,81)



vmedt=weim(vmed1,91)
vsitut=weim(vsitu1,61)


umedt=weim(umed1,91)
usitut=weim(usitu1,61)



plt.plot(dates.num2date(timevec),vmedt, 'red', label='PNBOIA')
plt.plot(dates.num2date(timevec),vsitut, 'blue', label='ROMS')
ax = plt.gca()
ax.legend(loc='best')
plt.show()


plt.plot(dates.num2date(timevec),umedt, 'red',label='PNBOIA')
plt.plot(dates.num2date(timevec),usitut, 'blue',  label='ROMS')
ax = plt.gca()
ax.legend(loc='best')
plt.show()

from scipy import stats
from sklearn.metrics import mean_squared_error as mse

stats.pearsonr(vmedt,vsitut)

rmsev=np.sqrt(mse(vmedt,vsitut))
print(rmsev)


stats.pearsonr(umedt,usitut)

rmseu=np.sqrt(mse(umedt,usitut))
print(rmseu)



from scipy import stats
from sklearn.metrics import mean_squared_error as mse

stats.pearsonr(vmedt,vsitutnest)

rmsev=np.sqrt(mse(vmedt,vsitutnest))
print(rmsev)


stats.pearsonr(umedt,usitutnest)

rmseu=np.sqrt(mse(umedt,usitutnest))
print(rmseu)


from scipy import stats
from sklearn.metrics import mean_squared_error as mse

stats.pearsonr(vmedt,vsitutdad)

rmsev=np.sqrt(mse(vmedt,vsitutdad))
print(rmsev)


stats.pearsonr(umedt,usitutdad)

rmseu=np.sqrt(mse(umedt,usitutdad))
print(rmseu)





vmedt=weim(vmed,81)
umedt=weim(umed,81)
vsitut=weim(vsitu,31)
usitut=weim(usitu,31)
vsitutdad=weim(vbeca,11)
usitutdad=weim(ubeca,11)
vsitutnest=weim(vson, 61)
usitutnest=weim(uson, 61)

plt.style.use('ggplot')

fig, axs = plt.subplots(2, sharex=True, figsize=(9,6))
#fig.suptitle('Vertically stacked subplots')
#axs[0].plot(dates.num2date(timevec),vsitut, 'r--', label='V-component MERCATOR')
#axs[0].plot(dates.num2date(timevec),vsitutdad, 'green',linestyle='--', label='V-component ROMS PARENT')
axs[0].plot(dates.num2date(timevec),vsitutdad, 'green',linestyle='--', label='V-component ROMS')
#axs[0].plot(dates.num2date(timevec),vsitutnest, 'black',linestyle='--', label='V-component ROMS NEST')
axs[0].plot(dates.num2date(timevec),vmedt, 'blue', label='V-component PNBOIA')
legend=axs[0].legend(loc=2, fontsize='xx-small')
legend.get_frame().set_facecolor('grey')
#axs[0].set_ylim([-0.3, 0.3])
axs[0].tick_params(labelsize=8)



#axs[1].plot(dates.num2date(timevec),usitut, 'r--',  label='U-component MERCATOR')
#axs[1].plot(dates.num2date(timevec),usitutdad, 'green',linestyle='--',  label='U-component ROMS PARENT')
axs[1].plot(dates.num2date(timevec),usitutdad, 'green',linestyle='--',  label='U-component ROMS')
#axs[1].plot(dates.num2date(timevec),usitutnest, 'black',linestyle='--', label='U-component ROMS NEST')
axs[1].plot(dates.num2date(timevec),umedt, 'blue',label='U-component PNBOIA')
axs[1].legend(loc=2)
legend=axs[1].legend(loc=2, fontsize='xx-small')
legend.get_frame().set_facecolor('grey')
#axs[1].set_ylim([-0.5, 0.3])
axs[1].tick_params(labelsize=8)


fig.text(0.06, 0.5, 'Velocity (m/s)', ha='center', va='center', rotation='vertical', fontsize=11)
plt.xticks(fontsize=7,rotation=35)
plt.gcf().subplots_adjust(bottom=0.15)
#fig.text(0.5, 0.9,'Depth = ' + str(float(zc)) + ' m',  fontsize=12, ha='center', va='center')
fig.text(0.5, 0.9,'Depth = ' + '5.5' + ' m',  fontsize=12, ha='center', va='center')

plt.savefig('vit_fundo.png', dpi=200, transparent=False)


plt.show()





############################################################################################## Mooring


from vgrid import s_coordinate, s_coordinate_2, s_coordinate_4
from netCDF4 import Dataset 
from scipy.interpolate import griddata, interp1d
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.pylab import *
from matplotlib import dates
from mpl_toolkits.axes_grid1 import make_axes_locatable
import glob
import xarray as xr

#lista = sorted(glob.glob('ocean_BRSE_his_b5_000[0-9]*'))
lista = sorted(glob.glob('R:/Modelos/BRSE_2014_2016/RESULTADOS/ocean_BRSE_his_b1_0[3-4][0-9][0-9]*'))

avgfile = xr.open_mfdataset(lista, concat_dim='ocean_time')


hh=np.array(avgfile['ocean_time'][:].dt.strftime('%Y-%m-%d  %H:00:00'))

hhdates=dates.datestr2num(hh)

fname_grd = 'BRSE_2012_GRD.nc'     #CF 1/36

tlst=list(np.arange(0,hh.shape[0],1))

## Load ROMS grid.
grd = Dataset(fname_grd)
x_roms = grd.variables['lon_rho'][:]
y_roms = grd.variables['lat_rho'][:]
msk_roms = grd.variables['mask_rho'][:]
msk_romsv = grd.variables['mask_v'][:]
h_roms = grd.variables['h'][:]
sh2 = msk_roms.shape
etamax, ximax = sh2

x_roms=x_roms[1:-1,1:-1]
y_roms=y_roms[1:-1,1:-1]

lat=np.array([-20.1])
lon=np.array([-39.4])


ltlatlon=abs(y_roms - lat)
lglatlon=abs(x_roms - lon)
latlon=ltlatlon + lglatlon
ltmin=int(np.where(latlon == latlon.min())[0])
lgmin=int(np.where(latlon == latlon.min())[1])

theta_b = 0.4
theta_s = 5.0
tcline = 3.
klevels = 30
Vtransform = 1
Vstretching = 1
Spherical = True

lst=list(np.arange(0,30))

if Vstretching==4:
  scoord = s_coordinate_4(h_roms, theta_b, theta_s, tcline, klevels)   #zeta is not used in the computation 
elif Vstretching==2:
  scoord = s_coordinate_2(h_roms, theta_b, theta_s, tcline, klevels)
elif Vstretching==1:
  scoord = s_coordinate(h_roms, theta_b, theta_s, tcline, klevels)

zr = -scoord.z_r[:]

zr=zr[lst,1:-1,1:-1] 

zc=np.array([50,150, 370,800])


zc=zc[::-1]


latv=np.array(avgfile['lat_v'][:])
lonv=np.array(avgfile['lon_v'][:])
lonu=np.array(avgfile['lon_u'][:])
latu=np.array(avgfile['lat_u'][:])

#uavg=np.array(avgfile.u.isel(s_rho=lst).isel(ocean_time=tlst).values)

#uavg=np.array(avgfile.u.isel(s_rho=lst).groupby('ocean_time.month').mean().values)



#uavg = 0.5*(uavg[:,:,:,1:]+uavg[:,:,:,:-1])
lonu = 0.5*(lonu[:,1:]+lonu[:,:-1])
latu = 0.5*(latu[:,1:]+latu[:,:-1])


#uavg=uavg[:,:,1:-1,:]
lonu=lonu[1:-1,:]
latu=latu[1:-1,:]

##np.array(avgfile.u.isel(s_rho=lst).isel(ocean_time=[1,2]).values)

#vavg=np.array(avgfile.v.isel(s_rho=lst).isel(ocean_time=tlst).values)

vavg=np.array(avgfile.v.isel(s_rho=lst).groupby('ocean_time.month').mean().values)


vavg = 0.5*(vavg[:,:,1:,:]+vavg[:,:,:-1,:])
latv = 0.5*(latv[1:,:]+latv[:-1,:])
lonv = 0.5*(lonv[1:,:]+lonv[:-1,:])

vavg=vavg[:,:,:,1:-1]
lonv=lonv[:,1:-1]
latv=latv[:,1:-1]


#tempavg=np.array(avgfile.temp.isel(s_rho=lst).isel(ocean_time=tlst).values)
#tempavg=tempavg[:,:,1:-1,1:-1]

ktl=3

#uavg=uavg[:,:,ltmin-ktl:ltmin+ktl, lgmin-ktl:lgmin+ktl]
vavg=vavg[:,:,ltmin-ktl:ltmin+ktl, lgmin-ktl:lgmin+ktl]
#tempavg=tempavg[:,:,ltmin-ktl:ltmin+ktl, lgmin-ktl:lgmin+ktl]
x_roms=x_roms[ltmin-ktl:ltmin+ktl, lgmin-ktl:lgmin+ktl]
y_roms=y_roms[ltmin-ktl:ltmin+ktl, lgmin-ktl:lgmin+ktl]


intu=np.zeros([vavg.shape[0],len(zc),x_roms.shape[0], x_roms.shape[1]])

intv=np.zeros([vavg.shape[0],len(zc),x_roms.shape[0], x_roms.shape[1]])

itemp=np.zeros([vavg.shape[0],len(zc),x_roms.shape[0], x_roms.shape[1]])

#zeta=avgfile['zeta'][:]

for j in range(intu.shape[2]):
  for k in range(intu.shape[3]):
    if (zr[-1,j,k] > zc.min()):
      zr[-1,j,k] = zc.min()

zr=zr[:,ltmin-ktl:ltmin+ktl, lgmin-ktl:lgmin+ktl]

UNDEF=np.nan

for i in range(intu.shape[0]):
  for j in range(intu.shape[2]):
    for k in range(intu.shape[3]):
#      intu[i,:,j,k] = np.interp(-zc, -zr[:,j,k], uavg[i,:,j,k], right=UNDEF, left=UNDEF)
      intv[i,:,j,k] = np.interp(-zc, -zr[:,j,k], np.ma.masked_invalid(vavg[i,:,j,k]), right=UNDEF, left=UNDEF)
#      itemp[i,:,j,k] = np.interp(-zc, -zr[:,j,k], tempavg[i,:,j,k], right=UNDEF, left=UNDEF)

intu=np.squeeze(intu)
intv=np.squeeze(intv)
itemp=np.squeeze(itemp)


#intvv=np.ma.masked_invalid(intv[[0,1,2,9,10,11],:].mean(axis=0))

intvv=np.ma.masked_invalid(intv.mean(axis=0))
############################################################
vsitu=np.zeros(len(zc))
usitu=np.zeros(len(zc))
lat=np.array([-20.1])
lon=np.array([-39.45])

for i in range(len(vsitu)):
  vsitu[i]=griddata((x_roms.ravel(),y_roms.ravel()), intvv[i,:].ravel(), (lon,lat))
#  usitu[i]=griddata((x_roms.ravel(),y_roms.ravel()), intu[i,:].ravel(), (lon,lat))

lon=np.array([-39.40])

for i in range(len(vsitu[0:2])):
  vsitu[i]=griddata((x_roms.ravel(),y_roms.ravel()), intvv[i,:].ravel(), (lon,lat))
#  usitu[i]=griddata((x_roms.ravel(),y_roms.ravel()), intu[i,:].ravel(), (lon,lat))


vstd=np.zeros(len(zc))
#ustd=np.zeros(len(zc))

for i in range(len(vsitu)):
  vstd[i]=griddata((x_roms.ravel(),y_roms.ravel()), intv[i,:].ravel(), (lon,lat))
  ustd[i]=griddata((x_roms.ravel(),y_roms.ravel()), intu[i,:].ravel(), (lon,lat))


vsituM=np.array([0.29,0.21,0.11,-0.1])
uerr=np.array([0.08,0.07,0.09,0.17])

marker_style = dict(color='tab:grey',marker='o',
                    markersize=12, markerfacecoloralt='tab:grey')
                    
fig, ax1 = plt.subplots(figsize=(5,7))
ax1.errorbar(vsituM*100, -zc, xerr=uerr*100,  **marker_style, linewidth=2, label='DADOS')

marker_style = dict(color='tab:red',marker='o',
                    markersize=12, markerfacecoloralt='tab:red')

uerr=np.array([0.07,0.08,0.1,0.16])
                    
ax1.errorbar(vsitu*100, -zc-10, xerr=uerr*100, **marker_style,  linewidth=2, label='MODELO')

ax1.set_xlim([-40,40])
ax1.set_ylim([-850,0])
ax1.set_xlabel('Velocidade (cm/s)', fontsize=14)
ax1.set_ylabel('Profundidade (m)',fontsize=14)

ax1.set_xticks([-20,0,20])
ax1.grid(alpha=0.5)

#legend=ax1.legend( fontsize='small', loc='lower center', ncol=2)
legend=ax1.legend(loc=3, fancybox=True, framealpha=1, shadow=True, borderpad=1, fontsize='small')

#legend.get_frame().set_facecolor('grey')
#axs[1].set_ylim([-0.5, 0.3])
ax1.tick_params(labelsize=12)

plt.savefig('m1.png', dpi=200, bbox_inches='tight', linestyle='.', transparent=False)

##################################################map


h_roms=h_roms[1:-1,1:-1]


umean=u.mean(axis=0)
vmean=v.mean(axis=0)
sp=4
ly=16

lon1=x_roms.copy()
lat1=y_roms.copy()

tim=0

for tim in [tim]:
  sp=6
  up=umean[ly,:,:]
  vp=vmean[ly,:,:]
  uu=up
  vv=vp
  val=np.sqrt((uu**2)+(vv**2))
  nlim=-15.5
  slim=-23
  wlim=-41
  elim=-33
  fig, ax1 = plt.subplots(figsize=(8,8))
  map = Basemap(projection='merc', llcrnrlat=slim, urcrnrlat=nlim,llcrnrlon=wlim, urcrnrlon=elim,resolution='l')
  map.drawcoastlines(linewidth=0.25)
  map.drawcountries(linewidth=0.25)
  map.fillcontinents(color='silver',lake_color='white')
  parallels = np.arange(-50,-9,1)
  map.drawparallels(parallels,labels=[1,0,0,1], linewidth=0.0)
  meridians = np.arange(-65,-15,1)
  map.drawmeridians(meridians,labels=[1,0,0,1], linewidth=0.0)
#  map.readshapefile('/mnt/c/Users/Fernando/Desktop/shape_unid_fed/lim_unidade_federacao_a', 'lim_unidade_federacao_a')
  map.readshapefile('/mnt/c/Users/Gabriel/Desktop/boundary_ini/shape_unid_fed/lim_unidade_federacao_a', 'lim_unidade_federacao_a')
  map.drawmapscale(-35., -22, -35, -22, 100, barstyle='fancy', fontsize = 11, yoffset=8000)
  x_roms, y_roms = map(lon1,lat1)
#
  a=ax1.pcolor(x_roms,y_roms,val, cmap=plt.get_cmap('viridis'), vmax=0.5)
  ax1.quiver(x_roms[0:-1:sp, 0:-1:sp],y_roms[0:-1:sp, 0:-1:sp],uu[0:-1:sp, 0:-1:sp], vv[0:-1:sp, 0:-1:sp], alpha=1)
  ax1.contourf(x_roms,y_roms,h_roms,levels=[0,750],colors=('gainsboro'))
  ax1.contour(x_roms,y_roms,h_roms,levels=[750],colors=('black'), linewidts=2)
#  plt.text(-49.5,-17,figdates[tim].strftime("%Y/%b/%d - %-I %p"), fontsize=10, fontweight='bold',
#        bbox={'facecolor': 'grey', 'alpha': 0.5, 'pad': 5})
  divider = make_axes_locatable(ax1)
  #cax = divider.append_axes("right", size="5%", pad=0.05)
  cax = fig.add_axes([0.91, 0.3, 0.02, 0.38])
  cbar=fig.colorbar(a, shrink=0.8, extend='both', ax=ax1, cax=cax)
  cbar.ax.set_ylabel('Velocidade (m/s)', rotation=270)
  cbar.ax.get_yaxis().labelpad = 11
  cbar.ax.tick_params(labelsize=9)
  text = cbar.ax.yaxis.label
  font = matplotlib.font_manager.FontProperties(family='times new roman', style='normal', size=12)
  text.set_font_properties(font)

plt.savefig('corrente_tub.png', dpi=200, transparent=False)

#plt.savefig('cor_tub.png', dpi=200, bbox_inches='tight', transparent=False)
