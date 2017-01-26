#!/usr/bin/env p
import sys
import datetime
import json
import urllib
# import pdb
import codecs

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

FARE_CLASSES = {
    'Main ': 'economy',
    'Delta': 'business',
    'First': 'firstclass'
}


def get_delta_price(orgn, dest, searchdate, returndate=None, passenger=1):
    """
    Scrape Delta.com and return price dictionary.
    For roundtrip, it scrapes twice as 2 oneways.
    Return 2 dictionary; one for departure and the other for return.
    key format is same as QPX.
    Additionally it returns the price according to the cabin.
    e.g) u'DL2830@DL1878@--': {'firstclass': u'USD511.10', 'business': u'USD290.95', 'economy': u'USD251.60'}
    It takes about 23 seconds for oneway, 37 for roundtrip
    """
    url = "http://www.delta.com/"   
    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true','--ssl-protocol=any','--load-images=false'])
    driver.set_window_size(1120, 1080)  
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

    try:
        # print (datetime.datetime.now() - start_time).seconds, '@@@'
        driver.get(url)
        WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.ID, "oneWayBtn")))
        oneway = driver.find_element_by_id('oneWayBtn')
        driver.execute_script("arguments[0].click();", oneway)
        driver.execute_script("document.getElementById('originCity').setAttribute('value', '"+orgn.strip()+"')")
        # origin = driver.find_element_by_id("originCity")
        # origin.clear()
        # origin.send_keys(orgn.strip())
        driver.execute_script("document.getElementById('destinationCity').setAttribute('value', '"+dest.strip()+"')")
        # destination = driver.find_element_by_id("destinationCity")
        # destination.send_keys(dest.strip())
        ddate = driver.find_element_by_id("departureDate")  
        driver.execute_script("document.getElementById('departureDate').setAttribute('value', '"+str(searchdate)+"')")
        driver.find_element_by_id("findFlightsSubmit").send_keys(Keys.ENTER)
    except:
        print "before data page"
        # display.stop()
        driver.quit()
        return {}, {}

    departure_price = get_price(driver)
    driver.quit()
    return departure_price

    return_price = {}

    if returndate:
        try:
            driver.get(url)
            WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.ID, "oneWayBtn")))
            oneway = driver.find_element_by_id('oneWayBtn')
            driver.execute_script("arguments[0].click();", oneway)
            driver.execute_script("document.getElementById('originCity').setAttribute('value', '"+dest.strip()+"')")
            # origin = driver.find_element_by_id("originCity")
            # origin.clear()
            # origin.send_keys(dest.strip())
            driver.execute_script("document.getElementById('destinationCity').setAttribute('value', '"+orgn.strip()+"')")
            # destination = driver.find_element_by_id("destinationCity")
            # destination.clear()
            # destination.send_keys(orgn.strip())
            ddate = driver.find_element_by_id("departureDate")  
            ddate.clear()
            ddate.send_keys(returndate.strip())
            # driver.execute_script("$('#departureDate').val('"+returndate+"');")
            driver.find_element_by_id("findFlightsSubmit").send_keys(Keys.ENTER)
            return_price = get_price(driver)
        except Exception, e:
            pass

    driver.quit()
    # print departure_price
    # print return_price
    return departure_price, return_price            


def get_price(driver):
    delta_price = {}

    try:
        WebDriverWait(driver,5).until(EC.presence_of_element_located((By.ID, "submitAdvanced")))
        print "no data"
        return delta_price
    except:
        print "Data found"

    try:
        WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.ID, "showAll-footer")))
        print "More than one page"
        driver.execute_script("""
            DWRHandler.currentPage = -1;
            var _shopInputDo=shopInputDo;
            shoppingUtil.scrollWindow("top");
            FilterFunctions.showFilterMsg();
            FlightUtil.emptyResults();
            ResummarizeFlightResultsDWR.pageResults(DWRHandler.currentPage, _shopInputDo.currentSessionCheckSum, delta.airShopping.cacheKey, {
            async: true,
            callback: function(searchResults) {
                if (searchResults != null) {
                    var jsonData = {};
                    jsonData['jsonobj'] = JSON.stringify(searchResults);
                    var cabininfo = document.getElementsByClassName('tblHeadUp')[0].innerHTML;
                    jsonData['cabinTypes'] = cabininfo;
                    localStorage.setItem('deltaData', JSON.stringify(jsonData));
                    var element = document.createElement('div');
                    element.id = "submitAdvanced";
                    element.appendChild(document.createTextNode("text"));
                    document.body.appendChild(element);
                    throw new Error("Results found");
                    if (searchResults.errorFwdURL == null) {
                        jsonResultPopulation(searchResults);
                        paginationPopulation(searchResults);
                        if (shoppingUtil.isIE8()) {
                            if (DWRHandler.currentPage == -1) {
                                ieTimeout = setTimeout("RenderTemplate.renderResult();FilterFunctions.hideFilterMsg();RenderTemplate.adjustHeight();", 200);
                            } else {
                                ieTimeout = setTimeout("RenderTemplate.renderResult();FilterFunctions.hideFilterMsg();RenderTemplate.adjustHeight();", 100);
                            }
                        } else {
                            RenderTemplate.renderResult();
                            FilterFunctions.hideFilterMsg();
                            RenderTemplate.adjustHeight();
                        }
                        if (DWRHandler.currentPage == -1) {
                            $("#showAll").hide();
                            $("#showAll-footer").hide();
                        }
                        contienuedOnload(false);
                        if (searchResults.debugInfo != null && ((typeof(printRequestResponse) !== "undefined") && printRequestResponse == true)) {
                            $("#requestXml").text(searchResults.debugInfo.itaRequest);
                            $("#responceXml").text(searchResults.debugInfo.itaResponse);
                            $("#reqRes").show();
                        }
                    } else {
                        window.location.replace(searchResults.errorFwdURL);
                    }
                } else {
                    FilterFunctions.errorHandling();
                }
                $(".tableHeaderHolderFareBottom.return2Top").show();
            },
            exceptionHandler: FilterFunctions.errorHandling
        });
        """)
    except:
        print "single page"
        try:
            driver.execute_script("""
            var sortBy = "deltaScheduleAward" ;
            SearchFlightResultsDWR.searchResults(currentSessionCheckSum, sortBy[0], delta.airShopping.numberOfColumnsToRequest, delta.airShopping.cacheKey, {
                async: true,
                timeout: 65000,
                callback: function(searchResults) {
                        var jsonData = {};
                        
                        jsonData['jsonobj'] = JSON.stringify(searchResults);
                        var cabininfo = document.getElementsByClassName('tblHeadUp')[0].innerHTML;
                        jsonData['cabinTypes'] = cabininfo;
                        localStorage.setItem('deltaData', JSON.stringify(jsonData));
                        var element = document.createElement('div');
                        element.id = "submitAdvanced";
                        element.appendChild(document.createTextNode("text"));
                        document.body.appendChild(element);
                        throw new Error("Results found");
                        
                    if (searchResults.errorFwdURL == null || searchResults.errorFwdURL == "") {
                        flightResultsObj.isDOMReady(searchResults, action, false);
                        FilterFunctions.hideFilterMsg();
                    } else {
                    
                        flightResultsObj.isDOMReady(searchResults, false, true);
                    }
                    if (!action) {
                        Wait.hide();
                        $(".tableHeaderHolderFareBottom").show();
                        $("#nextGenAirShopping .tableHeaderHolder").show();
                    }
                },
                errorHandler: function(msg, exc) {
                    shoppingUtil.errorHandler(msg, exc);
                },
                exceptionHandler: function(msg, exc) {
                    (action) ? FilterFunctions.hideFilterMsg(): "";
                    shoppingUtil.exceptionHandler(msg, exc);
                }
            });
            
            """)
        except:
            return delta_price
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "submitAdvanced")))
        result = driver.execute_script(""" return localStorage.getItem('deltaData'); """)
        deltaObj = json.loads(result)
        searchResult = json.loads(deltaObj['jsonobj'])
        flightData = searchResult["itineraries"]
    except:
        return delta_price
    

    for item in flightData:
        flight_code = ''
        for flight in item['slices'][0]['flights']:
            flight_code += flight['legs'][0]['marketAirline']['airline']['airlineCode'] + flight['legs'][0]['marketAirline']['flightNbr'] + '@'
        flight_code += '--'
    
        delta_ = {}
        for class_ in item['totalFare']:
            if class_['currencyCode']:
                price = class_['currencyCode']+class_['totalForAllPaxLeft'].replace(',','')+class_['totalForAllPaxRight']
                cabin = class_['cabinName'][:5]
                if cabin in FARE_CLASSES.keys():
                    delta_[FARE_CLASSES[cabin]] = price
                else:
                    class_['cabinName']
        delta_price[flight_code] = delta_

    return delta_price            


if __name__=='__main__':
    # pdb.set_trace()
    start_time = datetime.datetime.now()
    print get_delta_price('bos', 'sfo', '12/23/2016', '12/29/2016')
    # get_delta_price('msp', 'tlv', '12/26/2016')
    print (datetime.datetime.now() - start_time).seconds, '###'
