# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 10:35:00 2024

@author: Dr Carlos Moreno

"""
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def TrajPlot(df, fps, vid, ext): 
    
    mpl.rcParams['lines.markersize'] = 2
    
    scale = 0.17677
    
    img_name = vid.replace(ext,"jpg")
    img = mpimg.imread(img_name)
        
    df['time'] = df.frame/fps
        
    print('\n\tDrawing plots...\n')
        
    plt.rcParams['image.cmap'] = 'gnuplot'
    fig = plt.figure(figsize=(10, 3.4))
    fig.suptitle(f'Experimento: {experiment}')
    spec = fig.add_gridspec(ncols=2, nrows=1, left=0.05 , right=0.051 , hspace=0.1 , wspace=0.1)
    ax00 = fig.add_subplot(spec[0,0])
    for itm in df['item'].unique():
        data_plt = df[(df['item']==itm)].dropna()
        center_plt = [(x*scale,y*scale) for x,y in data_plt.center]
 
        ax00.plot(*zip(*center_plt))
        ax00.set_xlabel(r'X ($\mu$m)')
        ax00.set_ylabel(r'Y ($\mu$m)')
        
    names = [f'{itm}' for itm in list(df.item.unique())]
    ax00.legend(names)
    ax00.set_xlim(xmin=0, xmax=1920*scale) 
    ax00.set_ylim(1080*scale, 0)
        
    ax01 = fig.add_subplot(spec[0,1])
    ax01.imshow(img)
    formatter = lambda x, pos: f'{(x * 2 * scale):.0f}'  # scale is the resolution
    ax01.xaxis.set_major_formatter(formatter)
    ax01.yaxis.set_major_formatter(formatter)
    ax01.set_xlabel(r'X ($\mu$m)')
    ax01.set_ylabel(r'Y ($\mu$m)')
            
    plt.close(fig)  

if __name__ == '__main__':
    vid_analyzer()