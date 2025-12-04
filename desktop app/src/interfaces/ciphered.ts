export interface CiphPassword {
    email: string,
    login: string,
    password: string,
    domena: string,
    tfa: string,
    attachments: string[],
    id: string
}

export interface CiphNotes {
    name: string,
    content: string,
    attachments: string[],
    id: string
}

export interface CiphLicense {
    name: string,
    divers: {name:string, value:string}[],
    attachments: string[],
    id: string
}

export interface CiphIdentity {
    name: string,
    surname: string,
    IDnumber: string,
    country: string,
    state: string,
    city: string,
    street: string,
    number: string,
    attachemnts: string[],
    id: string
}

export interface CiphCreditCard {
    bankName: string,
    number: string,
    brand: string,
    CVV: string,
    owner: string,
    expDate: string,
    attachments: string[],
    id: string
}

export interface CiphAttachment {
    name: string,
    extension: string,
    id: string
}