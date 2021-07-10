# QuoteMaker - Markov chain quote generator

## Examples
![Example 1](https://user-images.githubusercontent.com/32440038/125172556-48fe8480-e1b2-11eb-9d4a-2b305becd519.png)  
![Example 2](https://user-images.githubusercontent.com/32440038/125172540-397f3b80-e1b2-11eb-9560-709071516ecc.png)  
![Example 3](https://user-images.githubusercontent.com/32440038/125172528-2f5d3d00-e1b2-11eb-99d7-cd0599fe50a7.png)  

## Brief
This is a simple quote generator made using Markov chains.  
The model is trained of a dataset provided by http://thewebminer.com so most of the credit goes to them.  
Background images are retrieved from Unsplash but the program could easily be adapted to load iamges locally.   

## Installation
```
virtualenv venv  
pip install -r requirements.txt  
python -m spacy download en_core_web_sm  
```

## Usage
```
python quotemaker.py  
```
