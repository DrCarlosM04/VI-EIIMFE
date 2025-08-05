# -*- coding: utf-8 -*-
#"""
#Created on Fri Mar 15 13:44:39 2024
#@author: C Moreno
#"""
import sys
import math
import pandas as pd
import numpy as np
import datetime
from tqdm import tqdm
import cv2
from skimage.measure import label, regionprops
#from scipy.ndimage import binary_fill_holes as bfh
import warnings
warnings.filterwarnings("ignore")


def p_tracker(file_in):
    
    # Abre el archivo de video    
    frame_name = file_in.replace("avi","jpg")
    vid = cv2.VideoCapture(file_in)

    
    # count the number of frames 
    frames = vid.get(cv2.CAP_PROP_FRAME_COUNT) 
    fps = vid.get(cv2.CAP_PROP_FPS) 
    seconds = round(frames / fps) 
    video_time = datetime.timedelta(seconds=seconds)
    
    T = " "*21
    print("\n")
    print(T+"#####################################")
    print(T+"#                                   #")
    print(T+"#    Beginning video measurement    #")
    print(T+"#                                   #")
    print(T+"#####################################\n")
    s = (80-9-len(file_in))//2
    print(' '*s+'File:\t{}\n'.format(file_in))
    s = (80-13-len(str(video_time)))//2
    print(' '*s+'Duration:\t{}\n'.format(video_time))
    

    pbar = tqdm(total=frames, unit=' frames', colour='green', position=0, leave=True, ncols=80)
    
    # inicia variables necesarias para el bucle
    count = 0
    
    tracking_objects = {}
    
    track_id = 0
    
    values = {'item':[],'center':[],'major':[], 'minor':[],'frame':[]}

    # Radio de búsqueda en múltiplos del radio de partícula
    search_radius = 1
    
    # Bucle principal iterando cada cuadro del video
    while(vid.isOpened()):
        ret, frame = vid.read()
        count += 1
        pbar.update(1)
    
    # Continuar durante todos los cuadros del video
        if ret == True:
          
    # Definir la variable con los puntos centrales de cada objeto en cada cuadro
            values_cur_frame = {'center':[],'major':[],'minor':[]}
        
    # Convertir a escala de grises
    # Disminuir el ruido suavizando con un filtro bilateral 
    # Calcular el valor medio de intensidad de pixel para determinar el umbral de binarizado
    # Binarizar la imagen de acuerdo a un valor medio de intensidad de pixel
            g_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)               
            s_frame = cv2.bilateralFilter(g_frame,15,30,100)
            ret,t_frame = cv2.threshold(s_frame, 0, 255, cv2.THRESH_OTSU)
            
    # Obtener el largo y ancho del cuadro
    # Etiquetar las zonas cerradas identificadas en el cuadro
    # Obtener un objeto que mida distintas propiedades de las zonas cuando se invoca
            s0,s1 = t_frame.shape
            # Labeled frame
            l_frame = label(t_frame)
            regions = regionprops(l_frame)
            
    # Solo objetos con  área mayor a 200 px serán medidos
    # Obtener las coordenadas del rectángulo que encierra a la partícula
    # Obtener las coordenadas del céntro de la partícula
    # Agregar las coordenadas del centro a la lista de objetos a seguir
            for props in regions:
    
                if props.area > 200:
                    #print(circ, props.area)
                    y0,x0,y1,x1 = props.bbox
    
                    c1,c0 = props.centroid
    
                    values_cur_frame['center'].append((c0,c1))
                    values_cur_frame['major'].append(props.axis_major_length)
                    values_cur_frame['minor'].append(props.axis_minor_length)
                    #cv2.rectangle(frame,(x0,y0),(x1,y1),(0,255,0),2)
                    #cv2.circle(frame,(int(c0),int(c1)),10,(255,0,0),-1)
    
    
            if count < 2:
                item=0
                for pt in values_cur_frame['center']:
    
                    tracking_objects[track_id] = pt
                    values['item'].append(track_id)
                    values['center'].append(values_cur_frame['center'][item])
                    values['major'].append(values_cur_frame['major'][item])
                    values['minor'].append(values_cur_frame['minor'][item])
                    values['frame'].append(count)
                    track_id +=1
                    item +=1
            else:
    
                
                tracking_objects_copy = tracking_objects.copy()
                values_cur_frame_copy = values_cur_frame.copy()
                
                for object_id, pt2 in tracking_objects_copy.items():
                    
                    for pt in values_cur_frame_copy['center']:
                        distance = math.hypot(pt2[0] - pt[0], pt2[1] - pt[1])
                        idx = values_cur_frame['center'].index(pt)
                        major = values_cur_frame['major'][idx]
                        
                        if distance < search_radius*major:
                            tracking_objects[object_id] = pt
                            values['item'].append(object_id)
                            values['center'].append(values_cur_frame['center'][idx])
                            values['major'].append(values_cur_frame['major'][idx])
                            values['minor'].append(values_cur_frame['minor'][idx])
                            values['frame'].append(count)
                            
                           
                            if pt in values_cur_frame['center']:
                                idx = values_cur_frame['center'].index(pt)
                                values_cur_frame['center'].pop(idx)
                                values_cur_frame['major'].pop(idx)
                                values_cur_frame['minor'].pop(idx)
                                continue

    
                for object_id, pt in tracking_objects.items():
                    pt_int = (int(pt[0]),int(pt[1]))
                    cv2.circle(frame,pt_int,5,(255,255,0),-1)
                    cv2.putText(frame,str(object_id), (pt_int[0],pt_int[1] - 15), 0, 2, (0,0,255), 3)
                    
                    
                frame = cv2.resize(frame, (s1//2,s0//2), fx = 0.1, fy = 0.1)
                cv2.imshow(file_in, frame)
                #s_frame = cv2.resize(s_frame, (s1//2,s0//2), fx = 0.1, fy = 0.1)
                #cv2.imshow("filter", s_frame)
                #t_frame = cv2.resize(t_frame, (s1//2,s0//2), fx = 0.1, fy = 0.1)
                #cv2.imshow("threshold", t_frame)
                
                if count == 2:
                    cv2.imwrite(frame_name, frame)
                
            
            if cv2.waitKey(25) & 0xFF == ord('q'):

                break
        
            #input("Press Enter to continue...")
        
        else:
            break
        
    pbar.close()  
    
    # Pad lists with NaN to ensure equal length
    max_len = max(len(v) for v in values.values())
    for key in values:
        missing = max_len - len(values[key])
        if missing > 0:
        # Handle tuple lists (like 'center') differently to preserve dtype
            if key == 'center':
                values[key].extend([(np.nan, np.nan)] * missing)  # or [(np.nan, np.nan)] if you prefer
            else:
                values[key].extend([np.nan] * missing)

    values_df = pd.DataFrame.from_dict(values)
    
    vid.release()
    cv2.destroyAllWindows()
    return values_df, fps


if __name__ == '__main__':
    p_tracker(sys.argv[1])
