# Media stream

**Endpoint:** `/api/admin/status/v1/participant/<id>/media_stream/`

## Fields

| Field | Type | Description |
|---|---|---|
| `end_time` | datetime | Indicates the time the media stream was stopped. |
| `id` | string | The primary key. |
| `node` | string | The Conferencing Node used for the media stream. Maximum length: 50 characters. |
| `rx_bitrate` | integer | The quantity of data currently being received by the Conferencing Node from the endpoint, in kilobits per second. |
| `rx_codec` | string | The format used by the endpoint to encode the media stream being sent to the Conferencing Node. |
| `rx_fps` | float | The framerate used by the endpoint to encode the media stream being sent to the Conferencing Node. |
| `rx_jitter` | float | The variation in the expected periodic arrival of packets being received by the Conferencing Node from the endpoint, in milliseconds. |
| `rx_packet_loss` | float | The percentage of packets sent from the endpoint but not received by the Conferencing Node. |
| `rx_packets_lost` | integer | The total quantity of packets sent from the endpoint but not received by the Conferencing Node. |
| `rx_packets_received` | integer | The total quantity of packets received by the Conferencing Node from the endpoint since the start of the conference. |
| `rx_resolution` | string | The resolution of the stream being received by the Conferencing Node from the endpoint. |
| `rx_windowed_packet_loss` | float | The percentage of packets sent from the endpoint but not received by the Conferencing Node. |
| `start_time` | datetime | Indicates the time the media stream was started. |
| `tx_bitrate` | integer | The quantity of data currently being sent from the Conferencing Node to the endpoint, in kilobits per second. |
| `tx_codec` | string | The format used by the Conferencing Node to encode the media stream being sent to the endpoint. |
| `tx_fps` | float | The framerate of the stream received from the remote Conferencing Node. |
| `tx_jitter` | float | The variation in the expected periodic arrival of packets being sent from the Conferencing Node to the endpoint, in milliseconds. |
| `tx_packet_loss` | float | The percentage of packets sent from the Conferencing Node but not received by the endpoint. |
| `tx_packets_lost` | integer | The total quantity of packets sent from the Conferencing Node but not received by the endpoint. |
| `tx_packets_sent` | integer | The total quantity of packets sent from the Conferencing Node to the endpoint since the start of the conference. |
| `tx_resolution` | string | The resolution of the stream being sent from the Conferencing Node to the endpoint. |
| `tx_windowed_packet_loss` | float | The percentage of packets sent from the Conferencing Node but not received by the endpoint. |
| `type` | string | Indicates the type of the media stream. audio: Audio media stream. video: Video media stream. presentation: Presentation media stream. |
