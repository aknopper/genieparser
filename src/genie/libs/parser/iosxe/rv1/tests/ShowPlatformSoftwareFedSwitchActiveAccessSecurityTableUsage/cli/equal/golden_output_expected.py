expected_output = {
    "feature":{
        "Default-Client":{
            "asic":{
                0:[
                    {
                        "mask":"Port-VLAN",
                        "maximum":4096,
                        "in_use":0,
                        "total_allocated":0,
                        "total_freed":0
                    },
                    {
                        "mask":"Port",
                        "maximum":4096,
                        "in_use":0,
                        "total_allocated":4,
                        "total_freed":4
                    }
                ],
                1:[
                    {
                        "mask":"Port-VLAN",
                        "maximum":4096,
                        "in_use":0,
                        "total_allocated":0,
                        "total_freed":0
                    },
                    {
                        "mask":"Port",
                        "maximum":4096,
                        "in_use":1,
                        "total_allocated":32,
                        "total_freed":31
                    }
                ]
            }
        },
        "Dot1x-MAC-Drop":{
            "asic":{
                0:[
                    {
                        "mask":"Port-VLAN-MAC",
                        "maximum":4096,
                        "in_use":0,
                        "total_allocated":0,
                        "total_freed":0
                    }
                ],
                1:[
                    {
                        "mask":"Port-VLAN-MAC",
                        "maximum":4096,
                        "in_use":0,
                        "total_allocated":0,
                        "total_freed":0
                    }
                ]
            }
        },
        "MAC-Client":{
            "asic":{
                0:[
                    {
                        "mask":"Port-VLAN-MAC",
                        "maximum":4096,
                        "in_use":0,
                        "total_allocated":0,
                        "total_freed":0
                    },
                    {
                        "mask":"Port-MAC",
                        "maximum":4096,
                        "in_use":0,
                        "total_allocated":0,
                        "total_freed":0
                    },
                    {
                        "mask":"MAC",
                        "maximum":4096,
                        "in_use":0,
                        "total_allocated":0,
                        "total_freed":0
                    }
                ],
                1:[
                    {
                        "mask":"Port-VLAN-MAC",
                        "maximum":4096,
                        "in_use":0,
                        "total_allocated":0,
                        "total_freed":0
                    },
                    {
                        "mask":"Port-MAC",
                        "maximum":4096,
                        "in_use":0,
                        "total_allocated":0,
                        "total_freed":0
                    },
                    {
                        "mask":"MAC",
                        "maximum":4096,
                        "in_use":0,
                        "total_allocated":0,
                        "total_freed":0
                    }
                ]
            }
        },
        "Secure-MAC":{
            "asic":{
                0:[
                    {
                        "mask":"Port-VLAN-MAC",
                        "maximum":4096,
                        "in_use":0,
                        "total_allocated":10,
                        "total_freed":10
                    },
                    {
                        "mask":"Port-MAC",
                        "maximum":4096,
                        "in_use":0,
                        "total_allocated":0,
                        "total_freed":0
                    }
                ],
                1:[
                    {
                        "mask":"Port-VLAN-MAC",
                        "maximum":4096,
                        "in_use":4,
                        "total_allocated":47,
                        "total_freed":43
                    },
                    {
                        "mask":"Port-MAC",
                        "maximum":4096,
                        "in_use":0,
                        "total_allocated":0,
                        "total_freed":0
                    }
                ]
            }
        }
    }
}