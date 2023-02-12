//
//  HttpClockApiHelper.swift
//  textual_clock_companion
//
//  Created by Samuel Chassot on 08.02.23.
//

import Foundation
import SwiftUI

struct RgbColor: Encodable, Decodable {
    let color_r: Int
    let color_g: Int
    let color_b: Int
    static func toUIColor(rgbColor:RgbColor) -> Color {
        return  Color(red: Double(rgbColor.color_r)/255.0, green: Double(rgbColor.color_g)/255.0, blue: Double(rgbColor.color_b)/255.0)
    }
    static func fromUIColor(uiColor:Color) -> RgbColor {
        let arrRgb = UIColor(uiColor).cgColor.components!
        return RgbColor(color_r: Int(arrRgb[0]*255.0), color_g: Int(arrRgb[1]*255), color_b: Int(arrRgb[2]*255))
    }
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
        print(try? JSONDecoder().decode(RgbColor.self, from: payload!))
        let url = URL(string: "http://\(clockAddress)/color")!
        var urlRequest = URLRequest(url: url)
        urlRequest.timeoutInterval = 3
        urlRequest.addValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpMethod = "POST"
        urlRequest.httpBody = payload
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
        let config = URLSessionConfiguration.ephemeral
        let session = URLSession(configuration: config)
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
        task.resume()
    }
    
}
