//
//  HttpClockApiHelper.swift
//  textual_clock_companion
//
//  Created by Samuel Chassot on 08.02.23.
//

import Foundation
struct RgbColor: Encodable, Decodable {
    let color_r: Double
    let color_g: Double
    let color_b: Double
}

struct LivenessMessage: Decodable {
    let liveness: Bool
}


struct HttpClockApiUtility {
    // Send an HTTP POST request to the /color
    static func sendColorUpdate(clockAddress: String, color: RgbColor, onSuccess: @escaping (String) -> Void, onError: @escaping (String) -> Void) -> Void{
        let payload = try? JSONEncoder().encode(color)
        if(payload == nil){
            onError("Cannot encode the given payload!")
            return
        }
        let url = URL(string: "http://\(clockAddress)/color")!
        var urlRequest = URLRequest(url: url)
        urlRequest.addValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpMethod = "POST"
        sendRequest(request: urlRequest, onSuccess: {(data) in
            onSuccess("Color update successful!")
        }, onError: onError)
        
    }
    static func getCurrentColor(clockAddress: String, onSuccess: @escaping (RgbColor) -> Void, onError: @escaping (String) -> Void) -> Void {
        let url = URL(string: "http://\(clockAddress)/color")!
        var urlRequest = URLRequest(url: url)
        urlRequest.addValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpMethod = "GET"
        sendRequest(request: urlRequest, onSuccess: {(data) in
            let rgbColor = try? JSONDecoder().decode(RgbColor.self, from: data)
            if(rgbColor == nil){
                onError("Cannot decode the received color!")
            }else{
                onSuccess(rgbColor!)
            }
            
        }, onError: onError)
    }
    
    static func sendRebootCommand(clockAddress: String,onSuccess: @escaping (String) -> Void, onError: @escaping (String) -> Void){
        let payload = try? JSONEncoder().encode(["reboot": "yes"])
        if(payload == nil){
            onError("Cannot encode the json payload!")
            return
        }
        let url = URL(string: "http://\(clockAddress)/reboot")!
        var urlRequest = URLRequest(url: url)
        urlRequest.addValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpMethod = "POST"
        sendRequest(request: urlRequest, onSuccess: {(data) in
            onSuccess("Reboot command sent!")
        }, onError: onError)
    }
    
    static func checkLiveness(clockAddress: String, onSuccess: @escaping (LivenessMessage) -> Void, onError: @escaping (String) -> Void) -> Void {
        let url = URL(string: "http://\(clockAddress)/liveness")!
        var urlRequest = URLRequest(url: url)
        urlRequest.addValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpMethod = "GET"
        sendRequest(request: urlRequest, onSuccess: {(data) in
            let msg = try? JSONDecoder().decode(LivenessMessage.self, from: data)
            if(msg == nil){
                onError("Cannot decode the received liveness message!")
            }else{
                onSuccess(msg!)
            }
        }, onError: onError)
    }
    
    private static func sendRequest(request:URLRequest, onSuccess: @escaping (Data) -> Void, onError: @escaping (String) -> Void){
        // Create the HTTP request
        let session = URLSession.shared
        let task = session.dataTask(with: request) { (data, response, error) in
            
            if let error = error {
                // Handle HTTP request error
                onError(error.localizedDescription)
            } else if let data = data {
                // Handle HTTP request response
                onSuccess(data)
            } else {
                // Handle unexpected error
                onError("Unexpected error occured.")
            }
        }
    }
    
}
