
var map;
var service;
var infowindow;

function initMap() {
  var pyrmont = new google.maps.LatLng(34.78085971236495, 137.1759605011184);

  map = new google.maps.Map(document.getElementById('map'), {
    center: pyrmont,
    zoom: 15,
    streetViewControl: false
  });
  

  document.getElementById('search').addEventListener('click', function() {

          var place = document.getElementById('keyword').value;
          var geocoder = new google.maps.Geocoder();      // geocoderのコンストラクタ

          geocoder.geocode({
            address: place
          }, function(results, status) {
            if (status == google.maps.GeocoderStatus.OK) {

              var bounds = new google.maps.LatLngBounds();

              for (var i in results) {
                if (results[0].geometry) {
                  // 緯度経度を取得
                  var latlng = results[0].geometry.location;
                  nearbysearch(latlng)
                }
              }
            } else if (status == google.maps.GeocoderStatus.ZERO_RESULTS) {
              alert("見つかりません");
            } else {
              console.log(status);
              alert("エラー発生");
            }
          });
        })
  document.getElementById('clear').addEventListener('click', function() {
    deleteMakers();
  });

}


function createMarker(latlng, icn, place)
{
  var marker = new google.maps.Marker({
    position: latlng,
    map: map
  });

  var placename = place.name;
  // 吹き出しにカフェの名前を埋め込む		  
  var contentString = `<div class="sample"><p id="place_name">${placename}</p></div>`;

  // 吹き出し
  var infoWindow = new google.maps.InfoWindow({ // 吹き出しの追加
  content:  contentString// 吹き出しに表示する内容
  });


  marker.addListener('click', function() { // マーカーをクリックしたとき
    infoWindow.open(map, marker); // 吹き出しの表示
  });

}

function deleteMakers() {
  if(marker != null){
    marker.setMap(null);
  }
  marker = null;
}

// 周辺のカフェを検索
function nearbysearch(pyrmont) {
    var request = {
      location: pyrmont,
      radius: '15000',
      type: ['campground']
    };

    service = new google.maps.places.PlacesService(map);
    service.nearbySearch(request, callback);

    function callback(results, status) {
      if (status == google.maps.places.PlacesServiceStatus.OK) {
        //取得したカフェ情報をそれぞれcreateMarkerに入れて、マーカーを作成  
        for (var i = 0; i < results.length; i++) {
          var place = results[i];
          //console.log(place)
          var latlng = place.geometry.location;
          var icn = place.icon;

          createMarker(latlng, icn, place);
        }
      }
    }
}
