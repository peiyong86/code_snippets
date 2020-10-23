This package include 2 modules: postprocess and tracking.

postprocess module provide post processing function for OCR results of single image.
Concatenate sperated text boxes which belongs to the same line.
Replace "(" ")" "，" and "。" with empty string.

tracking module provide tracking function for a series of OCR result(tipycaly the OCR results 
from video frames). 
Tracking of text boxes is based on spatical overlap and temporal adjection of text boxes,
and duplicated texts are removed based on edit distance and char features of Chinese 
characters.


