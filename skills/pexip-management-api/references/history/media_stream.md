# Media stream

**Endpoint:** `/api/admin/history/v1/media_stream/`

## Allowed methods

- **Allowed Methods:** GET

## Fields

| Field | Type | Description |
|---|---|---|
| `end_time` | datetime | Indicates the time the media stream was ended. |
| `id` | integer | The primary key. |
| `node` | string | The Conferencing Node used for the media stream. Maximum length: 50 characters. |
| `participant` | `participant` (related resource) | The participant for the media stream. |
| `resource_uri` | string | The URI that identifies this resource. |
| `rx_bitrate` | integer | The quantity of data received by the Conferencing Node from the endpoint, in kilobits per second. |
| `rx_codec` | string | The format used by the endpoint to encode the media stream sent to the Conferencing Node. |
| `rx_fps` | float | The framerate of the stream received by the Conferencing Node from the endpoint. |
| `rx_packet_loss` | float | The percentage of packets sent from the endpoint but not received by the Conferencing Node. |
| `rx_packets_lost` | integer | The total quantity of packets sent from the endpoint but not received by the Conferencing Node. |
| `rx_packets_received` | integer | The total quantity of packets received by the Conferencing Node from the endpoint. |
| `rx_resolution` | string | The resolution of the stream received by the Conferencing Node from the endpoint. |
| `start_time` | datetime | Indicates the time the media stream was started. |
| `stream_id` | string | The primary key. |
| `stream_type` | string | Indicates the type of the media stream. audio: Audio media stream. video: Video media stream. presentation: Presentation media stream. |
| `tx_bitrate` | integer | The quantity of data sent from the Conferencing Node to the endpoint, in kilobits per second. |
| `tx_codec` | string | The format used by the Conferencing Node to encode the media stream that was sent to the endpoint. |
| `tx_fps` | float | The framerate of the stream received from the remote Conferencing Node. |
| `tx_packet_loss` | float | The percentage of packets sent from the Conferencing Node but not received by the endpoint. |
| `tx_packets_lost` | integer | The total quantity of packets sent from the Conferencing Node but not received by the endpoint. |
| `tx_packets_sent` | integer | The total quantity of packets sent from the Conferencing Node to the endpoint. |
| `tx_resolution` | string | The resolution of the stream that was sent from the Conferencing Node to the endpoint. |
