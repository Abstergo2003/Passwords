const namesToImages = {
  password: 'basic_world.svg',
  creditCard: 'ecommerce_creditcard.svg',
  identity: 'basic_eye.svg',
  license: 'basic_postcard.svg',
  notes: 'basic_todo.svg'
}

const generalDataStructure = {
    "password" : [],
    "creditCard": [],
    "identity": [],
    "license": [],
    "notes": []
}

String.prototype.capitalizeFirst = function() {
    return this.slice(0,1).toUpperCase() + this.slice(1, this.length)
}

function hasNumber(str:string) {
    return /\d/.test(str);
}

function hasSpecialCharacter(str:string) {
    return /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(str);
}

function hasCapitalLetter(str:string) {
    return /[A-Z]/.test(str);
}

function isLongerThan(str:string, length:number) {
    return  str.length >= length
}

function getSiteName(str:string) {
    str = str.replace('https://', '').replace('http://', '')
    const index = str.indexOf('.')
    if (index != -1) {
        str = str.slice(0, index)
    }

    return str.capitalizeFirst()
}

function capitalizeFirst(str:string) {
  return str.capitalizeFirst()
}

function checkPasswordStandards(password: string) {
  if (!hasCapitalLetter(password)) {
      return 'Password must contain capital letter!!!';
    }
    else if (!hasNumber(password)) {
      return 'Password must contain number!!!';
    }
    else if (!hasSpecialCharacter(password)) {
      return 'Password must contain special character!!!';
    }
    else if (!isLongerThan(password, 12)) {
      return 'Password must be longer or equal 12 characters!!!';
    } else {
      return '';
    }
}

const delay = (delayInms: number) => {
    return new Promise(resolve => setTimeout(resolve, delayInms));
}

export {namesToImages, generalDataStructure, hasNumber, hasSpecialCharacter, hasCapitalLetter, isLongerThan, getSiteName, capitalizeFirst, checkPasswordStandards, delay}