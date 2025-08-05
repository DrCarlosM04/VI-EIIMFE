# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 10:35:00 2024

@author: Dr Carlos Moreno

This file provides the routines necesary to the analysis of the videos obtained
from the electrodeformation experiments. It is capable of obtaining the name of 
all the videos for analysis in the folder, those files must have the same file
extension in order to be detected by this program.
"""
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from os import makedirs, rename
from glob import glob
#import logging
from Particle_tracker import p_tracker

#logger = logging.getLogger('ED_analysis')
#logging.basicConfig(level=logging.INFO, filename="ED_Analysis.log",format="%(asctime)s - %(levelname)s - %(message)s", datefmt='%m/%d/%Y %I:%M:%S %p')


def vid_analyzer(ext='avi'): 
    
    mpl.rcParams['lines.markersize'] = 2
    
    # Reads all the files in the folder containing videos of experiments and 
    # creates a list with the names in it to use for iteration.
    files = sorted(glob('*' + ext))
    
    # Name all the folders to organize the results
    processed = 'Done/'
    makedirs(processed, exist_ok=True)
    measurement = 'Measurement_Results/'
    makedirs(measurement, exist_ok=True)
    graphs = 'Plots/'
    makedirs(graphs, exist_ok=True)
    msg_init = """\tI've created new folders called '{}' to contain the
  results of the video analysis and '{}' to contain the plots
  generated with the data of all detected particles.
    """.format(measurement,graphs)
    print(msg_init)
             
    scale = 0.17677

    
    for vid in files:
        
        # Analisis de video
        df, fps = p_tracker(vid)
        
        EXP = vid.replace('.avi', '')
        img_out = vid.replace('avi','jpg')
        
        print('\nAnalysing video: {}...'.format(EXP))
        
        experiment = vid.replace(".avi","")
        results_DF = vid.replace("avi","csv")
        img_name = vid.replace("avi","jpg")
        img = mpimg.imread(img_name)
        
        
        df['time'] = df.frame/fps
        df[['item','center','frame','time']].to_csv(measurement + results_DF, index=False)
        
        print('\n\tDrawing plots...\n')
        
        plt.rcParams['image.cmap'] = 'gnuplot'
        fig = plt.figure(figsize=(10, 3.4), layout="constrained")
        fig.suptitle(f'Experimento: {experiment}')
        spec = fig.add_gridspec(ncols=2, nrows=1, left=0.05 , right=0.051 , hspace=0.1 , wspace=0.1)
        ax00 = fig.add_subplot(spec[0,0])
        for itm in df['item'].unique():
            data_plt = df[(df['item']==itm)].dropna()
            center_plt = [(x*scale,y*scale) for x,y in data_plt.center]
            center_df = pd.DataFrame(center_plt,columns=['X','Y'])
            center_df = pd.concat([center_df,data_plt['time']],axis=1)
            center_df.to_csv(f'{EXP}-Particle_{itm}.csv',index=False)
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
            
        sumary_plot = vid.replace(".avi",f"{EXP}.png")
        plt.savefig(graphs + sumary_plot, bbox_inches='tight')
        plt.close(fig)  
        
        rename(img_out, measurement + img_out)
        rename(vid,processed + vid)
        
        
    
    msg_end = """\n\nAll done, and in case your missed it...\n
    \t  I've created new folders called '{}' to contain the 
    \tresults of the video analysis and '{}' to contain the plots
    \tgenerated with the data of all detected particles.
    \tPD: The videos are now in the {} folder.\n""".format(measurement,graphs,processed)
    print(msg_end)


if __name__ == '__main__':
    vid_analyzer()