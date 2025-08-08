def execute():
    return {
      '$mergeObjects': [
          {
              'keys': '$keys'
          }, {
              '$reduce': {
                  'input': '$keys', 
                  'initialValue': {
                      'allkeys': [], 
                      'projectkeys': [], 
                      'percentkeys': [], 
                      'calculatedkeys': []
                  }, 
                  'in': {
                      '$mergeObjects': [
                          '$$value', {
                              '$reduce': {
                                  'input': '$$this.children', 
                                  'initialValue': '$$value', 
                                  'in': {
                                      '$mergeObjects': [
                                          '$$value', {
                                              'allkeys': {
                                                  '$concatArrays': [
                                                      '$$value.allkeys', [
                                                          '$$this'
                                                      ]
                                                  ]
                                              }
                                          }, {
                                              'projectkeys': {
                                                  '$cond': [
                                                      {
                                                          '$eq': [
                                                              {
                                                                  '$ifNull': [
                                                                      '$$this.project', True
                                                                  ]
                                                              }, True
                                                          ]
                                                      }, {
                                                          '$concatArrays': [
                                                              '$$value.projectkeys', [
                                                                  '$$this.key'
                                                              ]
                                                          ]
                                                      }, '$$value.projectkeys'
                                                  ]
                                              }
                                          }, {
                                              'percentkeys': {
                                                  '$cond': [
                                                      {
                                                          '$eq': [
                                                              {
                                                                  '$ifNull': [
                                                                      '$$this.ispercent', False
                                                                  ]
                                                              }, True
                                                          ]
                                                      }, {
                                                          '$concatArrays': [
                                                              '$$value.percentkeys', [
                                                                  '$$this.key'
                                                              ]
                                                          ]
                                                      }, '$$value.percentkeys'
                                                  ]
                                              }
                                          }, {
                                              'calculatedkeys': {
                                                  '$cond': [
                                                      {
                                                          '$ne': [
                                                              {
                                                                  '$ifNull': [
                                                                      '$$this.subkeys', None
                                                                  ]
                                                              }, None
                                                          ]
                                                      }, {
                                                          '$concatArrays': [
                                                              '$$value.calculatedkeys', [
                                                                  '$$this.key'
                                                              ]
                                                          ]
                                                      }, '$$value.calculatedkeys'
                                                  ]
                                              }
                                          }
                                      ]
                                  }
                              }
                          }
                      ]
                  }
              }
          }
      ]
  }