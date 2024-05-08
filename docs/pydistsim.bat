@echo off
if NOT "%PYDISTSIM_ENV%" == "" ( call %PYDISTSIM_ENV%\Scripts\activate.bat )
ipython --pylab=qt --profile=pydistsim
