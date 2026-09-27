import axios from "axios" // Lub własny instancja api client

export async function setup2FA() {
  const response = await axios.post("api/2fa/setup")
  return response.data // Oczekuje { secret: string, qr_code_uri: string }
}

export async function enable2FA(code: string) {
  const response = await axios.post("api/2fa/enable", { code })
  return response.data
}

export async function disable2FA(code: string) {
  const response = await axios.post("api/2fa/disable", { code })
  return response.data
}