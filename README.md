# SDN-TESTING

# test 1 - Limitação de banda para a comunicação entre hosts para 100mb/s
  O primeiro teste tem como base testar a velocidade da banda do host 2 e 3 com o host 1, em que foi utilizado  o OFPMeterMod para setar a banda máxima para 100 mb/s e 1Gb/s. Também existe mais codigo de controlador chamado NS(Not shared) criado que adciona um OFPMeterMod adcional já que ao utilizar o mesmo meter_id toda aquela banda é compartilhada e, portanto, adciona mais uma limitação a comunicação entre os hosts e a tornando imprevisivel.
  Execução:
    NS - tende a manter a banda no definido (100 mb/s ou 1Gb/s)
    Normal - tende a compartilhar a banda máxima entre os hosts durante a execução simultanea.
  * Precisa que iperf3 esteja instalado.
  ***
# teste 2 - Corte de comunicação 
 O corte da comunicaçõa do host 2 é feito ao adcionar uma regra que quando o host 3 começa qualquer comunicação as comunicações do host 2 são descartas até que o host2 pare a comunicação.

# teste 3 -

